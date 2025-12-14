import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np
import warnings  # Import the warnings library

def main():
    # --- 1. Setup ---
    
    # GÜNCELLENMİŞ ÇIKTI KLASÖRÜ
    # r"..." kullanarak Windows yollarındaki \ karakterlerinin doğru okunmasını sağlıyoruz
    OUTDIR = Path(r"C:\Users\olgub\OneDrive\Masaüstü\uzaylı bulmaca\kopya tarihler dosyalar - Copy")
    
    FILE_NAME = 'focused_meta_comparison_results.csv'
    # We know the correct column name from the previous analysis
    COL_NAME = 'percentage_diff_of_5uj' 
    
    OUTDIR.mkdir(exist_ok=True) # Create output directory

    print(f"Reading file: '{FILE_NAME}'...")
    try:
        df = pd.read_csv(FILE_NAME, delimiter=';')
    except FileNotFoundError:
        print(f"ERROR: File not found: '{FILE_NAME}'. Please ensure the file is in the correct directory.")
        return
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return

    print("File read successfully.")

    # --- 2. Data Preparation ---
    print(f"Preparing column '{COL_NAME}' for analysis...")
    if COL_NAME not in df.columns:
        print(f"ERROR: Column '{COL_NAME}' not found.")
        return
    else:
        try:
            # The column is already 'float64' (numeric)
            all_values = df[COL_NAME].astype(float)
            all_values = all_values.dropna()
            
            if len(all_values) == 0:
                print(f"ERROR: No valid data found in column '{COL_NAME}'.")
                return

            print(f"Found {len(all_values)} valid 'percentage_diff' values.")
            print(f"Max 'percentage_diff' for all {len(all_values)} candidates: {all_values.max():.4f}%")

            # Sort values from smallest to largest
            all_values_sorted = all_values.sort_values()

            # --- UPDATE: 6 Groups (6 x 8 = 48 Points) ---
            print("Grouping the top 6 x 8 = 48 data points...")
            groups = {
                "Group 1 (Top 8)": (all_values_sorted.iloc[0:8], 'red', '--'),
                "Group 2 (Next 8)": (all_values_sorted.iloc[8:16], 'orange', ':'),
                "Group 3 (Next 8)": (all_values_sorted.iloc[16:24], 'green', '--'),
                "Group 4 (Next 8)": (all_values_sorted.iloc[24:32], 'blue', ':'),
                "Group 5 (Next 8)": (all_values_sorted.iloc[32:40], 'purple', '--'),
                "Group 6 (Next 8)": (all_values_sorted.iloc[40:48], 'brown', ':')
            }
            
            print("\n--- Values for Analysis ---")
            for name, (data, _, _) in groups.items():
                print(f"{name} (Min: {data.min():.6f}, Max: {data.max():.6f})")

            # --- 3. Plotting (2-Part Figure) ---
            print("\nGenerating plot...")
            with warnings.catch_warnings():
                # Suppress future warnings from seaborn's 'cut' parameter
                warnings.simplefilter("ignore", FutureWarning)
                
                fig, (ax1, ax2) = plt.subplots(
                    2, 1, 
                    figsize=(14, 12), 
                    gridspec_kw={'height_ratios': [1, 2]},
                    sharex=False # Let X-axes be independent
                )
                fig.suptitle(f"Cost Distribution (KDE) and 'Elbow' Analysis (N={len(all_values)})", fontsize=16, y=1.02)

                # --- Plot 1: Overview (0% - 1.5%) ---
                sns.kdeplot(all_values, fill=True, ax=ax1, color='blue', label=f'All Candidates Distribution (N={len(all_values)})', cut=0)
                ax1.set_title(f"Overview (Full Distribution, 0% - {all_values.max():.2f}%)")
                # GÜNCELLENMİŞ ETİKET
                ax1.set_xlabel("Percentage Difference (Applied Formula Matched)")
                ax1.set_ylabel("Density")
                ax1.set_xlim(0, 1.5) # Keep the 1.5% limit as requested
                ax1.legend()

                # --- Plot 2: Zoom-in ("Elbow" Region) ---
                sns.kdeplot(all_values, fill=True, ax=ax2, color='lightblue', label=f'All Candidates Distribution (N={len(all_values)})', cut=0)
                
                # Plot lines for all 6 groups
                for group_name, (data, color, style) in groups.items():
                    for i, val in enumerate(data):
                        label = group_name if i == 0 else "" # Only one label per group
                        ax2.axvline(val, color=color, linestyle=style, linewidth=1.2, label=label)

                # Adjust zoom limit based on the max value of the 6th group
                zoom_limit_val = groups["Group 6 (Next 8)"][0].max()
                zoom_limit = zoom_limit_val * 1.2 # Add 20% padding
                
                ax2.set_xlim(0, zoom_limit)
                ax2.set_title(f"'Elbow' Analysis (Zoom-in - Top 48 Points: 0% - {zoom_limit:.4f}%)")
                # GÜNCELLENMİŞ ETİKET
                ax2.set_xlabel("Percentage Difference (Applied Formula Matched)")
                ax2.set_ylabel("Density")
                ax2.legend()
                
                # --- Custom X-axis Ticks Code ---
                print("Adding custom X-axis ticks...")

                # Get the first values of Group 1 and Group 2
                val_g1 = groups["Group 1 (Top 8)"][0].min()
                val_g2 = groups["Group 2 (Next 8)"][0].min()
                
                # Get the auto-generated ticks
                current_ticks = ax2.get_xticks()
                
                # Add our special values to this list
                new_ticks = np.append(current_ticks, [val_g1, val_g2])
                
                # Clean up ticks outside our zoom limit
                new_ticks = new_ticks[new_ticks <= zoom_limit]
                
                # Sort and remove duplicates
                new_ticks = np.sort(np.unique(new_ticks))
                
                # Set the new combined tick list
                ax2.set_xticks(new_ticks)
                
                # Format labels to 5 decimal places
                new_labels = [f'{tick:.5f}' for tick in new_ticks]
                
                # Set new labels, rotated 90 degrees
                ax2.set_xticklabels(new_labels, rotation=90, fontsize=8)
                
                # Highlight our special ticks
                try:
                    # Find the index of our values in the new tick list
                    g1_index = np.where(np.isclose(new_ticks, val_g1))[0][0]
                    g2_index = np.where(np.isclose(new_ticks, val_g2))[0][0]
                    
                    # Color and bold the labels
                    ax2.get_xticklabels()[g1_index].set_color('red')
                    ax2.get_xticklabels()[g1_index].set_fontweight('bold')
                    ax2.get_xticklabels()[g2_index].set_color('orange')
                    ax2.get_xticklabels()[g2_index].set_fontweight('bold')
                except IndexError:
                    print("Warning: Could not highlight custom tick labels.")
                
                print("Custom X-axis ticks added.")
                
                plt.tight_layout()
            
            # --- KAYDETME BÖLÜMÜ (GÜNCELLENMİŞ YOL) ---
            # Artık OUTDIR değişkeni belirttiğin klasörü gösteriyor
            
            # 1. PNG olarak kaydet
            save_path_png = OUTDIR / "kde_elbow_analysis_top48_EN_v2.png"
            plt.savefig(save_path_png, dpi=300) 
            print(f"\nPlot successfully saved as '{save_path_png}'.")

            # 2. PDF olarak kaydet
            save_path_pdf = OUTDIR / "kde_elbow_analysis_top48_EN_v2.pdf"
            plt.savefig(save_path_pdf, format='pdf') 
            print(f"Plot successfully saved as '{save_path_pdf}'.")

        except KeyError:
            print(f"ERROR: Column '{COL_NAME}' not found. This is a code error.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

# This allows the script to be run directly
if __name__ == "__main__":
    main()