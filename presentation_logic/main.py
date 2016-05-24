# Created by: Dr. David John & Kenneth Meza.
# Created at: January, 2016.
# Updated at: May, 2016.

# LIBRARIES
from business_logic.models_functions import *
from business_logic.initialization_functions import *
from business_logic.mutation_functions import *
from business_logic.repair_functions import *
from business_logic.selection_functions import *
from copy import deepcopy
from data_logic.data_functions import *
import data_logic.data_input as data
import os
from presentation_logic.IO_functions import *


# ========
#   MAIN
# ========

# FUNCTION: main
def main():
    """ The main function program, having the structure of the SGA. """

    # Initial Variables
    pop_size = 250  # Population size
    num_genes = 12  # Amount of genes for each chromosome. The matrix's size will be: num_genes*num_genes
    per_ones = 5  # Percentage of 'ones' to put on every chromosome on the initial population, based on matrix's size
    likelihood_function = 1  # 1 = cotemporal, 2 = next_step_one, 3 = next_step_one_two
    per_elitism = 10  # Percentage of elitism
    selection_prop = 0.05  # Probability of selection
    mutation_prop = 0.3  # Probability of mutation
    num_mutations = 1  # Amount of mutations per chromosome
    per_filter_cm = 0.7  # Percentage for filtering values in the composite model
    per_filter_am = 0.7  # Percentage for filtering values in the amalgamated model
    num_matings = 500  # Amount of matings (generations)
    num_composite_model = 12  # Amount of composite models

    filter_likelihood_selection(likelihood_function)

    # The variable 'rep' can be found inside 'data_logic.data_input.py'. Refers to replications.
    data.rep = data_switcher(data.a_switch_log, data.a_switch_zscore, data.rep)  # log & zscore transforms

    # Pre-calculation of values
    num_survivors = calc_num_survivors(pop_size, per_elitism)

    print("=== SIMPLE GENETIC ALGORITHM ===\n")
    amalgamated_population = []  # contains the chromosomes that will be used for creating the amalgamated model
    for i in range(0, num_composite_model):
        print("* GENERATING COMPOSITE MODEL " + str(i+1))

        # Creation of the initial population using "seeding" method. See the function documentation.
        print("* Creating the initial population...")
        current_population = seed_population(pop_size, num_genes, per_ones, likelihood_function, data.rep)
        print("* Initial Population created, having " + str(len(select_uniques_chromosomes(current_population))) +
              " unique chromosomes.")

        for j in range(0, num_matings):
            print("* Working on generation " + str(j + 1) + "...")
            # 1) Given a sorted population, this function add ranks used on selection
            fitness_calculator(current_population)

            # 2) Creation of the new population, by doing the selection process
            new_population = selection_function(current_population, num_survivors, selection_prop)

            # 3) Application of the mutation function to the population
            mutation_function(new_population, mutation_prop, num_mutations)

            # 4) Application of the repairing function to the population
            current_population = repair_population(new_population)

            # 5) The applying of the likelihood on every chromosome to obtain the 'likelihood result'
            likelihood_result_calculator(current_population, likelihood_function, data.rep)

            # 6) Finding the 'relative likelihood result' for every chromosome
            relative_likelihood_result_calculator(current_population)

            # 7) Sorting of the population based on the 'likelihood result' of every chromosome
            relative_likelihood_result_sorting(current_population)

            print("\tcreated.")

        # Removing from the population the repeated chromosomes
        current_population = select_uniques_chromosomes(current_population)
        print("* The last generation ends with " + str(len(current_population)) + " unique chromosomes.")

        # Recalculation of 'likelihood' values and fitness on the current population (unique chromosomes)
        likelihood_result_calculator(current_population, likelihood_function, data.rep)
        relative_likelihood_result_calculator(current_population)
        relative_likelihood_result_sorting(current_population)
        fitness_calculator(current_population)

        # All the chromosomes in the unique current population are appended to the amalgamated population
        for chromosome in current_population:
            amalgamated_population.append(Chromosome(deepcopy(chromosome.get_genes())))

        # Creating and displaying of the composite model
        print("* Creating the composite model...")
        composite_model = model_creator(current_population, num_genes, likelihood_function)
        print("\tcreated.\n")

        view_model(composite_model, "COMPOSITE MODEL (ROUNDED TO 3 DECIMALS)")

        print("\n* Creating the image...")
        create_model_image(convert_model_to_digraph(composite_model, per_filter_cm, data.a_protein_names),
                           data.a_name + " - " + str(i + 1) + " (Composite Model)", likelihood_function)
        print("\tcreated.")

        print("* Creating the file...")
        write_matrix_file("../" + data.a_name + " - " + str(i + 1) + " (Composite Mode).txt", composite_model)
        print("\tcreated.")

        print("* Done.\n")

    print("...................................\n")

    print("* GENERATING AMALGAMATED MODEL")
    # Creating and displaying of the amalgamated model
    print("* Creating the amalgamated model...")

    likelihood_result_calculator(amalgamated_population, likelihood_function, data.rep)
    relative_likelihood_result_calculator(amalgamated_population)

    # Removing from the amalgamated population the repeated chromosomes
    amalgamated_population = select_uniques_chromosomes(amalgamated_population)
    print("\t\t- The amalgamated population ends with " + str(len(amalgamated_population)) + " unique chromosomes.")

    # Recalculation of 'likelihood' values and fitness on the amalgamated population (unique chromosomes)
    likelihood_result_calculator(amalgamated_population, likelihood_function, data.rep)
    relative_likelihood_result_calculator(amalgamated_population)
    relative_likelihood_result_sorting(amalgamated_population)
    fitness_calculator(amalgamated_population)

    # Creation of the folder where the amalgamated population's files are going to be stored
    if not os.path.exists("../Chromosomes for Amalgamated Model"):
        os.makedirs("../Chromosomes for Amalgamated Model")
    for i in range(0, len(amalgamated_population)):
        write_matrix_file("../Chromosomes for Amalgamated Model/Chromosome " + str(i+1) + ".txt", composite_model)

    amalgamated_model = model_creator(amalgamated_population, num_genes, likelihood_function)
    print("\tcreated.\n")

    view_model(amalgamated_model, "AMALGAMATED MODEL (ROUNDED TO 3 DECIMALS)")

    print("\n* Creating the image...")
    create_model_image(convert_model_to_digraph(amalgamated_model, per_filter_am, data.a_protein_names),
                       data.a_name + " (AMALGAMATED MODEL)", likelihood_function)
    print("\tcreated.")

    print("* Creating the file...")
    write_matrix_file("../" + data.a_name + " (AMALGAMATED MODEL).txt", amalgamated_model)
    print("\tcreated.")

    print("* Done.\n")
    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

if __name__ == "__main__":
    main()
