#include <iostream>
#include <string>
#include <nlohmann/json.hpp>  // Include JSON library

using json = nlohmann::json;

int main() {
    std::string input;
    std::getline(std::cin, input);  // Read JSON from stdin

    try {
        // Parse JSON
        json parsed_json = json::parse(input);

        // Only print valid JSON (no extra text)
        std::cout << parsed_json.dump() << std::endl;

    } catch (const json::parse_error& e) {
        std::cerr << "JSON parsing error: " << e.what() << std::endl;
        return 1;
    }

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
