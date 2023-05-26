import json, re, os, sys
from deep_translator import GoogleTranslator

INTERPOLATION_VARIABLE_PATTERN = r"(?<=\{\{)[^\{\}]*(?=\}\})"
DEFAULT_LANGUAGE = "en"
DEFAULT_DIR = ""


def exit_with_error(message):
    print(message)
    exit(1)


def get_directory(directory=""):
    return os.path.join(os.getcwd(), directory)


def get_file_name(lang_code):
    return f"{lang_code}.json"


def get_file_path(dir, lang_code):
    return os.path.join(get_directory(dir), get_file_name(lang_code))


def get_file_json(lang_code):
    try:
        return json.load(
            open(get_file_path(translation_dir, lang_code), encoding="utf-8")
        )
    except json.JSONDecodeError:
        if lang_code == from_language:
            exit_with_error(
                f"ERROR: Could not decode from language json file: {lang_code}.json"
            )
        print(
            f"Could not decode json file: {get_file_name(lang_code)}. Creating empty object"
        )
        return {}


def get_json_skeleton():
    """Returns the skeleton of the "from language" json file"""
    return get_file_json(from_language)


def save_file(lang_code, data):
    file_name = get_file_name(lang_code)
    file = get_file_path(translation_dir, lang_code)
    with open(file, "w", encoding="utf-8") as output_file:
        output_file.write(data)
        output_file.write("\n")
        output_file.close()
    print(f"Translated {file_name}")


def extract_language_codes_from_files(dir):
    """Extracts the language codes from the .json files in the directory"""
    try:
        language_codes = [
            filename.rsplit(".json")[0]
            for filename in os.listdir(dir)
            if filename.endswith(".json")
        ]
    except FileNotFoundError:
        exit_with_error(f"ERROR: Directory {dir} not found")

    if len(language_codes) == 0:
        exit_with_error("ERROR: No json files found in directory")

    return language_codes


def translate(value, language):
    """Translates the string"""
    return GoogleTranslator(source=from_language, target=language).translate(value)


def translate_interpolated_string(val, language):
    """Translates the string in the specified language, whilst maintaining the original interpolated variable names"""
    interpolated_vars = re.findall(INTERPOLATION_VARIABLE_PATTERN, val)
    interpolation_masked = re.sub(INTERPOLATION_VARIABLE_PATTERN, " ###### ", val)
    translation = translate(interpolation_masked, language)

    for interpolation in interpolated_vars:
        translation = translation.replace(" ###### ", interpolation, 1)

    return translation


def translate_string(language, val):
    """Translates the string in the specified language"""
    if "{{" in val:
        return translate_interpolated_string(val, language)
    else:
        return translate(val, language)


def translate_file(language):
    existing_translation = get_file_json(language)
    final_translation = get_json_skeleton()

    def translate_object(source, target):
        """
        Translates the keys from the existing object in the target object.
        Keys missing at the target object are added and translated
        Keys only present in target object are removed
        """

        for key, val_t in target.items():
            val_s = source.get(key)
            if isinstance(val_t, dict):
                if isinstance(val_s, dict):
                    translate_object(val_s, val_t)
                else:
                    translate_object({}, val_t)
            elif isinstance(val_t, str):
                if isinstance(val_s, str):
                    target[key] = val_s
                else:
                    target[key] = translate_string(language, val_t)

    translate_object(existing_translation, final_translation)

    translated_json = json.dumps(final_translation, indent=2, ensure_ascii=False)
    return translated_json


def translate_files_in_dir(dir):
    language_codes = extract_language_codes_from_files(dir)

    if from_language not in language_codes:
        exit_with_error(f"ERROR: Missing source language file: {from_language}.json")

    for lang_code in language_codes:
        if lang_code != from_language:
            translation = translate_file(lang_code)
            save_file(lang_code, translation)


if __name__ == "__main__":
    args = sys.argv

    dir = DEFAULT_DIR
    from_language = DEFAULT_LANGUAGE

    if len(args) > 1:
        dir = args[1].strip()
    if len(args) > 2:
        from_language = args[2].strip()

    translation_dir = get_directory(dir)
    translate_files_in_dir(translation_dir)
