#include <iostream>
#include <string>
#include <nlohmann/json.hpp>  // Include JSON library

using json = nlohmann::json;

int main() {
    std::string input;
    std::getline(std::cin, input);  // Read JSON from stdin

    // Parse JSON
    json parsed_json = json::parse(input);

    // Print key-value pairs
    std::cout << "Parsed JSON:\n";
    for (auto& [key, value] : parsed_json.items()) {
        std::cout << key << ": " << value << std::endl;
    }

    // Convert back to JSON and print
    std::cout << "\nReconstructed JSON:\n" << parsed_json.dump(4) << std::endl;

    return 0;
}



#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <cjson/cJSON.h>  // Include cJSON library

#define BUFFER_SIZE 1024

int main() {
    char buffer[BUFFER_SIZE];

    // Read JSON from stdin
    if (fgets(buffer, BUFFER_SIZE, stdin) == NULL) {
        fprintf(stderr, "Error reading input\n");
        return 1;
    }

    // Parse JSON
    cJSON *json = cJSON_Parse(buffer);
    if (json == NULL) {
        fprintf(stderr, "Error parsing JSON\n");
        return 1;
    }

    // Print key-value pairs
    cJSON *item = NULL;
    printf("Parsed JSON:\n");
    cJSON_ArrayForEach(item, json) {
        printf("%s: %s\n", item->string, cJSON_IsNumber(item) ? "Number" : item->valuestring);
    }

    // Convert back to JSON string and print
    char *json_string = cJSON_Print(json);
    printf("\nReconstructed JSON:\n%s\n", json_string);

    // Clean up
    free(json_string);
    cJSON_Delete(json);
    return 0;
}
