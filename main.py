from dotenv import load_dotenv
import os

from scripts.glom import GlomDatasetGenerator

load_dotenv()

def main():
    print("Available scripts:")
    print("1. glom.py generate_dataset")

    script_selection = input("\nEnter the number of the function you want to run: ")

    if script_selection == "1":
        api_key = os.getenv("LABELBOX_API_KEY")

        if api_key is None:
            print("\nLABELBOX_API_KEY is not provided in .env file")
            return

        generator = GlomDatasetGenerator(api_key)

        spec_selection = "specs/glom.ndjson"

        if not os.path.exists(spec_selection):
            print("Generating spec file...")
            generator.generate_spec(spec_selection)

        print("Generating dataset...")
        generator.generate_dataset(spec_selection)
        print("Done.")
    else:
        print("Invalid selection.")


if __name__ == "__main__":
    main()
