"""
Pipeline Human Predictome scanner

Refactored to use Predictomes interaction CSV.
Parsing of complex_name column into Protein_A, Protein_B, complex_length columns.
One-pass scan over interaction rows, extracting the ones that are of interest regarding
the input experimental dataset and LORF1/2 references.
Adding a tag to each extracted row, indicating whether it's a primary or secondary interaction.
For LORF reference interactions, the flag indicates which LORF(s) is (are) involved.


Core outputs:
1. predictomes_interactions_of_interest.csv
   - primary / secondary interactions involving experimental proteins
2. predictomes_LORF_reference_interactions.csv
   - all interactions involving LORF1_HUMAN and/or LORF2_HUMAN
3. primary_interactions_log.csv
   - longitudinal log for primary (LORF2) interactions
4. master.log
    - master log file for the pipeline run, reporting metadata in each step
"""


# 1. Imports

import pandas as pd
import logging
import argparse
import sys
import os
import re
import requests
import time



# 2. Argument parsing


def parse_args():
    parser = argparse.ArgumentParser(description="Predictomes interaction scanner v2")

    parser.add_argument("--data", required=True, help="Path to input experimental .xlsx file")
    parser.add_argument("--sheet_name", required=True, help="Sheet name inside the Excel file")
    parser.add_argument("--predictomes_csv", required=True, help="Predictomes interaction CSV")
    parser.add_argument("--out_dir", required=True, help="Output directory for pipeline results")

    return parser.parse_args()



# 3. Logging setup


def init_logging(master_log_path):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(message)s",
        handlers=[
            logging.FileHandler(master_log_path, mode="w"),
            logging.StreamHandler(sys.stdout)
        ]
    )



# 4. UniProt utilities


def up_entry_name_extractor(ID):
    """Fetch UniProt entry name from UniProt REST API."""
    url = f"https://rest.uniprot.org/uniprotkb/{ID}.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        time.sleep(0.1)
        return data.get("uniProtkbId", pd.NA)
    except Exception as e:
        logging.info(f"Error fetching {ID}: {e}")
        return pd.NA



# 5. Load experimental data


def load_data_add_uniprot_names(data_path, sheet_name):
    df = pd.read_excel(data_path, sheet_name=sheet_name, engine="openpyxl")
    df["UniProt_Entry_Name"] = df["Uniprot_clean"].apply(up_entry_name_extractor)

    n_total = len(df)
    n_fail = df["UniProt_Entry_Name"].isna().sum()

    logging.info(
        f"Experimental data loaded. Total proteins: {n_total}. "
        f"UniProt Entry Names resolved for {n_total - n_fail}/{n_total}."
    )

    return df



# 6. Primary interactions log


def generate_primary_interaction_log(experimental_df):
    primary_log = pd.DataFrame({
        "Protein_A_UniProt_Entry_Name": ["LORF2_HUMAN"] * len(experimental_df),
        "Protein_B_UniProt_Entry_Name": experimental_df["UniProt_Entry_Name"].values,
        "Complex_length_aa": [pd.NA] * len(experimental_df),
        "Predictomes_availability": [False] * len(experimental_df),
        "SPOC_score": [pd.NA] * len(experimental_df),
        #"Final_interaction_evaluation": [pd.NA] * len(experimental_df)
    })

    logging.info("Primary interactions log initialized.")
    return primary_log



# 7. Predictomes CSV parsing utilities


def parse_complex_name(complex_name):
    """
    Parse complex_name of the form:
    PROTA_HUMAN__PROTB_HUMAN__501aa
    """
    tokens = complex_name.split("__")
    if len(tokens) < 3:
        return pd.NA, pd.NA, pd.NA

    prot1, prot2 = tokens[0], tokens[1]

    length_match = re.search(r"(\d+)aa", tokens[2])
    length = int(length_match.group(1)) if length_match else pd.NA

    return prot1, prot2, length


def normalize_protein_order(p1, p2):
    """Ensure LORF2_HUMAN is Protein_A if present, else alphabetical."""
    if p1 == "LORF2_HUMAN":
        return p1, p2
    if p2 == "LORF2_HUMAN":
        return p2, p1
    return tuple(sorted([p1, p2]))


# 8. Core one-pass scanner


def scan_predictomes_interactions(predictomes_csv, experimental_set, primary_log):
    df = pd.read_csv(predictomes_csv)

    interactions_of_interest = []
    lorfx_reference = []

    logging.info(f"Scanning Predictomes CSV with {len(df)} interaction rows...")

    # Setting counters for logging 
    counter_LORF1 = 0
    counter_LORF2 = 0
    counter_LORF12 = 0
    counter_primary = 0
    counter_secondary = 0

    for _, row in df.iterrows():
        prot1, prot2, length = parse_complex_name(row["complex_name"])
        if pd.isna(prot1) or pd.isna(prot2):
            continue

        protA, protB = normalize_protein_order(prot1, prot2)

        # LORF reference capture 
        lorfx_flag = 0
        if "LORF1_HUMAN" in (protA, protB) and not "LORF2_HUMAN" in (protA, protB):
            lorfx_flag = 1
            counter_LORF1 += 1
        if "LORF2_HUMAN" in (protA, protB) and not "LORF1_HUMAN" in (protA, protB):
            lorfx_flag = 2 
            counter_LORF2 += 1
        if "LORF1_HUMAN" in (protA, protB) and "LORF2_HUMAN" in (protA, protB):
            lorfx_flag = 12
            counter_LORF12 += 1

        if lorfx_flag != 0:
            ref_row = row.copy()
            ref_row["Protein_A_UniProt_Entry_Name"] = protA
            ref_row["Protein_B_UniProt_Entry_Name"] = protB
            ref_row["Complex_length_aa"] = length
            ref_row["LORF_x_interaction"] = lorfx_flag
            lorfx_reference.append(ref_row)

        
        #  Interactions of interest 
        interaction_type = None
        if "LORF2_HUMAN" in (protA, protB):
            other = protB if protA == "LORF2_HUMAN" else protA
            if other in experimental_set:
                interaction_type = "primary"
                counter_primary += 1

        elif protA in experimental_set and protB in experimental_set:
            interaction_type = "secondary"
            counter_secondary += 1


        if interaction_type:
            int_row = row.copy()
            int_row["Protein_A_UniProt_Entry_Name"] = protA
            int_row["Protein_B_UniProt_Entry_Name"] = protB
            int_row["Complex_length_aa"] = length
            int_row["interaction_type"] = interaction_type
            interactions_of_interest.append(int_row)

            # update primary log immediately if applicable
            if interaction_type == "primary":
                mask = primary_log["Protein_B_UniProt_Entry_Name"] == protB
                primary_log.loc[mask, "Complex_length_aa"] = length
                primary_log.loc[mask, "Predictomes_availability"] = True
                primary_log.loc[mask, "SPOC_score"] = row.get("spoc_score", pd.NA)

    logging.info(f"Primary + secondary interactions captured: {len(interactions_of_interest)}")
    logging.info(f"  - Primary interactions: {counter_primary} | "
                 f"  - Secondary interactions: {counter_secondary}")
    
    logging.info(f"LORF reference interactions captured: {len(lorfx_reference)}")
    logging.info(f"  - LORF1 only: {counter_LORF1} | "
                 f"  - LORF2 only: {counter_LORF2} | "
                 f"  - LORF1+LORF2: {counter_LORF12} "
                 )

    return (
        pd.DataFrame(interactions_of_interest),
        pd.DataFrame(lorfx_reference),
        primary_log
    )



# 9. Main


def main():
    args = parse_args()

    out_dir = args.out_dir
    predictomes_subdir = f"{out_dir}/1_predictomes_scan"
    master_log_path = f"{out_dir}/master.log"

    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(predictomes_subdir, exist_ok=True)

    init_logging(master_log_path)

    logging.info("===== Predictomes pipeline v2 started =====")

    # Load experimental data
    experimental_df = load_data_add_uniprot_names(args.data, args.sheet_name)
    experimental_set = set(
        experimental_df["UniProt_Entry_Name"].dropna().astype(str).values
    )

    # Prepare primary interactions log
    primary_log = generate_primary_interaction_log(experimental_df)

    # Scan Predictomes CSV
    interactions_df, lorfx_df, primary_log = scan_predictomes_interactions(
        args.predictomes_csv,
        experimental_set,
        primary_log
    )

    # Save outputs
    interactions_df.to_csv(
        f"{predictomes_subdir}/predictomes_interactions_of_interest.csv",
        index=False
    )

    lorfx_df.to_csv(
        f"{predictomes_subdir}/predictomes_LORF_reference_interactions.csv",
        index=False
    )

    primary_log.to_csv(
        f"{predictomes_subdir}/primary_interactions_log.csv",
        index=False
    )

    logging.info("All outputs written to disk.")
    logging.info("===== Predictomes pipeline v2 completed =====")


if __name__ == "__main__":
    main()
