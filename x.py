
# Run the command and capture output
        try:
            self.result = subprocess.run(
                command,
                text=True,
                capture_output=True,
                check=True
            )
            # Read JSON output
            output = self.result.stdout.strip()  # Directly gets stdout as a string, can handle print also now
            parsed_data = json.loads(output)  # Convert JSON string to Python dict
            return parsed_data
        except subprocess.CalledProcessError as e:
            # Handle errors during execution
            errorMessage =  f"Error running command '{command}': {e.stderr or 'Unknown error'}"
            raise RuntimeError(errorMessage) from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Output Data not proper Json : {output}")
        except FileNotFoundError:
            raise RuntimeError(f"Command not found: {command}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {str(e)}") from e




import argparse, sys, json

def func(unknown_args):
    key_value_pairs = {}
    for i in range(0, len(unknown_args), 2):
        if unknown_args[i].startswith('--') and i + 1 < len(unknown_args):
            key = unknown_args[i].lstrip('--')
            value = unknown_args[i + 1]
            key_value_pairs[key] = value

    # Print all key-value pairs
    # for key, value in key_value_pairs.items():
    #     print(f"{key}: {value}")
    
    print(json.dumps(key_value_pairs))
        
if __name__ == "__main__":
    # Initialize ArgumentParser
    parser = argparse.ArgumentParser(description="Print all key-value pairs of arguments.")

    # Use the `parse_known_args()` method to handle arbitrary arguments
    # This will allow you to handle arguments dynamically without predefining them
    args, unknown_args = parser.parse_known_args()
    func(unknown_args)


#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[]) {
    printf("{");

    int first = 1;
    for (int i = 1; i < argc - 1; i += 2) {
        if (strncmp(argv[i], "--", 2) == 0) {  // Check for -- prefix
            if (!first) {
                printf(", ");
            }
            first = 0;
            printf("\"%s\": \"%s\"", argv[i] + 2, argv[i + 1]);
        }
    }

    printf("}\n");
    return 0;
}


#include <iostream>
#include <sstream>

int main(int argc, char *argv[]) {
    std::ostringstream json;
    json << "{";

    for (int i = 1; i < argc - 1; i += 2) {
        std::string key = argv[i];
        std::string value = argv[i + 1];

        if (key.rfind("--", 0) == 0) {  // Remove "--" prefix
            key = key.substr(2);
        }

        json << "\"" << key << "\": \"" << value << "\"";

        if (i + 2 < argc) {  // Add a comma if more pairs exist
            json << ", ";
        }
    }

    json << "}";

    // Write JSON string to stdout stream (not explicitly printing)
    std::cout << json.str() << std::endl;

    return 0;
}

nodeReturnValueFinal = {f"GID_{str(self._node.gid)}": nodeReturnValue}

        if 'upstreamResult' in kwargs.keys():
            x = kwargs['upstreamResult'] #list {gid_x : {status="",result={}}, }
            del kwargs['upstreamResult']
            for item in x:
                for _,v in item.items():
                    if v["result"]==None: continue
                    kwargs.update(**v["result"]) # Task specific results now part of all result, no differenciation, may change later
                                             # What are you doing with status



