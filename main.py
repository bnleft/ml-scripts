from scripts.glom import GlomDatasetGenerator

def main():
    print("Available scripts:")
    print("1. glom.py generate_dataset")

    script_selection = input("Enter the number of the function you want to run: ")

    if script_selection == "1":
        spec_selection = input("Enter the spec file location: ")

        generator = GlomDatasetGenerator(spec_selection)
        generator.generate_dataset()
    else:
        print("Invalid selection.")

if __name__ == "__main__":
    main()
