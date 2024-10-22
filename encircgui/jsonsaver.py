import json
from pathlib import Path

class JSONSaver:
    def __init__(self, base_filename, max_entries=1000):
        self.base_path = Path(base_filename).parent
        self.base_filename = Path(base_filename).name
        self.max_entries = max_entries
        self.current_file_index = 0
        self.current_entry_count = 0
        self.data_list = []
        
        # Ensure the directory for saving files exists
        self.base_path.mkdir(parents=True, exist_ok=True)

    def add_data(self, data_dict):
        """Add a new data dictionary to the current file."""
        self.data_list.append(data_dict)
        self.current_entry_count += 1
        
        if self.current_entry_count >= self.max_entries:
            self.save_to_file()
            self.current_entry_count = 0
            self.data_list = []

    def save_to_file(self):
        """Save the collected data to a new JSON file."""
        filename = self.base_path / f"{self.base_filename}_{self.current_file_index}.json"
        with open(filename, 'w') as json_file:
            json.dump(self.data_list, json_file, indent=4)
        
        self.current_file_index += 1
        print(f"Saved {len(self.data_list)} entries to {filename}")

    def close(self):
        """Save any remaining data before closing."""
        if self.data_list:
            self.save_to_file()


def main():
    # Example usage:
    saver = JSONSaver("data/measurement_data")

    for i in range(2500):
        data_dict = {
            "timestamp": i,
            "exposure": 100,
            "dataSum1": i * 1,
            "dataSum2": i * 2,
            "dataSum3": i * 3,
            "dataSum4": i * 4,
            "result": "OK" if i % 2 == 0 else "FAIL"
        }
        saver.add_data(data_dict)

    saver.close()


if __name__ == "__main__":
    main()