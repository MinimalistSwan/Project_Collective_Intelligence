import numpy as np
import pandas as pd
from scipy.stats import t

# Function to calculate t-statistic and p-value
def independent_t_test(mean1, std1, n1, mean2, std2, n2):
    # Calculate the t-statistic
    t_stat = (mean1 - mean2) / np.sqrt((std1**2 / n1) + (std2**2 / n2))
    
    # Calculate the degrees of freedom
    df = ((std1**2 / n1) + (std2**2 / n2))**2 / (((std1**2 / n1)**2 / (n1 - 1)) + ((std2**2 / n2)**2 / (n2 - 1)))
    
    # Calculate the p-value
    p_value = 2 * t.sf(np.abs(t_stat), df)
    
    return t_stat, p_value, df

# Load the data from the CSV files
with_flocking_df = pd.read_csv('Assignments/Assignment_2/Results/AvgEnergyFreeFlocking.csv')
no_flocking_df = pd.read_csv('Assignments/Assignment_2/Results/AvgEnergyFreeNoFlocking.csv')

# Extract the population values for each frame
fox_population_flocking = with_flocking_df['Fox']
rabbit_population_flocking = with_flocking_df['Rabbit']
fox_population_no_flocking = no_flocking_df['Fox']
rabbit_population_no_flocking = no_flocking_df['Rabbit']

# Calculate means and standard deviations
mean_fox_flocking = np.mean(fox_population_flocking)
std_fox_flocking = np.std(fox_population_flocking, ddof=1)
n_fox_flocking = len(fox_population_flocking)

mean_fox_no_flocking = np.mean(fox_population_no_flocking)
std_fox_no_flocking = np.std(fox_population_no_flocking, ddof=1)
n_fox_no_flocking = len(fox_population_no_flocking)

mean_rabbit_flocking = np.mean(rabbit_population_flocking)
std_rabbit_flocking = np.std(rabbit_population_flocking, ddof=1)
n_rabbit_flocking = len(rabbit_population_flocking)

mean_rabbit_no_flocking = np.mean(rabbit_population_no_flocking)
std_rabbit_no_flocking = np.std(rabbit_population_no_flocking, ddof=1)
n_rabbit_no_flocking = len(rabbit_population_no_flocking)

# Perform the t-tests for foxes and rabbits
t_stat_fox, p_val_fox, df_fox = independent_t_test(mean_fox_flocking, std_fox_flocking, n_fox_flocking,
                                                   mean_fox_no_flocking, std_fox_no_flocking, n_fox_no_flocking)

t_stat_rabbit, p_val_rabbit, df_rabbit = independent_t_test(mean_rabbit_flocking, std_rabbit_flocking, n_rabbit_flocking,
                                                            mean_rabbit_no_flocking, std_rabbit_no_flocking, n_rabbit_no_flocking)

# Output the results for foxes
print(f"Fox Population - t-statistic = {t_stat_fox:.2f}, p-value = {p_val_fox:.4f}, degrees of freedom = {df_fox:.2f}")

# Output the results for rabbits
print(f"Rabbit Population - t-statistic = {t_stat_rabbit:.2f}, p-value = {p_val_rabbit:.4f}, degrees of freedom = {df_rabbit:.2f}")

# Interpretation
alpha = 0.05
if p_val_fox < alpha:
    print("There is a significant difference in fox populations between flocking and no flocking scenarios.")
else:
    print("There is no significant difference in fox populations between flocking and no flocking scenarios.")

if p_val_rabbit < alpha:
    print("There is a significant difference in rabbit populations between flocking and no flocking scenarios.")
else:
    print("There is no significant difference in rabbit populations between flocking and no flocking scenarios.")