import pandas as pd
import numpy as np
import yaml
import hashlib

def load_config(config_file="config.yaml"):
    """Load YAML configuration file."""
    with open(config_file, "r") as f:
        return yaml.safe_load(f)

def hash_value(value, method="sha256"):
    """Hash a single value into a hex string."""
    if pd.isna(value):
        return value
    if method == "md5":
        return hashlib.md5(str(value).encode()).hexdigest()
    else:  # default sha256
        return hashlib.sha256(str(value).encode()).hexdigest()

def generate_synthetic_data(df, sensitive_fields, numeric_noise, categorical_strategy):
    synthetic_df = df.copy()
    
    for field, strategy in sensitive_fields.items():
        if field in synthetic_df.columns:
            if strategy == "hash":
                synthetic_df[field] = synthetic_df[field].apply(lambda x: hash_value(x, "sha256"))
            
            elif strategy == "numeric_noise" and np.issubdtype(synthetic_df[field].dtype, np.number):
                mean, std = synthetic_df[field].mean(), synthetic_df[field].std()
                if numeric_noise.get("method") == "uniform":
                    synthetic_df[field] = synthetic_df[field] + np.random.uniform(-std, std, len(df)) * numeric_noise.get("scale", 0.1)
                else:  # default normal
                    synthetic_df[field] = np.random.normal(mean, std * (1 + numeric_noise.get("scale", 0.1)), len(df))
    
    return synthetic_df

def main(config_file="config.yaml"):
    # Load config
    config = load_config(config_file)
    
    # Read input file
    df = pd.read_csv(config["input_file"])
    
    # Generate synthetic data
    synthetic_df = generate_synthetic_data(
        df,
        config["sensitive_fields"],
        config.get("numeric_noise", {}),
        config.get("categorical_strategy", {})
    )
    
    # Save output
    synthetic_df.to_csv(config["output_file"], index=False)
    print(f"Synthetic data saved to {config['output_file']}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Synthetic Data Generator")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to YAML config file")
    args = parser.parse_args()
    main(args.config)