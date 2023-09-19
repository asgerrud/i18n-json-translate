import json, re, os, sys
from deep_translator import GoogleTranslator
from progress.bar import Bar

INTERPOLATION_VARIABLE_PATTERN = r"(?<=\{\{)[^\{\}]*(?=\}\})"
DEFAULT_LANGUAGE = "en"
DEFAULT_DIR = ""


def exit_with_error(message):
    print(message)
    exit(1)


def get_directory(directory=""):
    return os.path.join(os.getcwd(), directory)


def get_file_name(language_code):
    return f"{language_code}.json"


def get_file_path(dir, language_code):
    return os.path.join(get_directory(dir), get_file_name(language_code))


def get_file_json(language_code):
    try:
        return json.load(
            open(get_file_path(translation_dir, language_code), encoding="utf-8")
        )
    except json.JSONDecodeError:
        if language_code == from_language:
            exit_with_error(
                f"ERROR: Could not decode from language json file: {language_code}.json"
            )
        print(
            f"Could not decode json file: {get_file_name(language_code)}. Creating empty object"
        )
        return {}


def get_json_skeleton():
    """Returns the skeleton of the "from language" json file"""
    return get_file_json(from_language)

def get_keys_total(json_object, count):
    for k, v in json_object.items():
        if isinstance(v, dict):
            return get_keys_total(v, count)
        else:
            count += 1
    return count

def save_file(data, language_code):
    file = get_file_path(translation_dir, language_code)
    with open(file, "w", encoding="utf-8") as output_file:
        output_file.write(data)
        output_file.write("\n")
        output_file.close()


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


def translate_string(text, language_code):
    """Translates the string"""
    if language_code == "sr":
        language_code = "hr"

    return GoogleTranslator(source=from_language, target=language_code).translate(text)


def translate_interpolated_string(text, language_code):
    """Translates the string in the specified language, whilst maintaining the original interpolated variable names"""
    interpolated_vars = re.findall(INTERPOLATION_VARIABLE_PATTERN, text)
    interpolation_masked = re.sub(INTERPOLATION_VARIABLE_PATTERN, " ###### ", text)
    translation = translate_string(interpolation_masked, language_code)

    for interpolation in interpolated_vars:
        translation = translation.replace(" ###### ", interpolation, 1)

    return translation


def translate(text, language_code):
    """Translates the string in the specified language"""
    if "{{" in text:
        return translate_interpolated_string(text, language_code)
    else:
        return translate_string(text, language_code)


def translate_file(language_code, index, files_total):
    existing_translation = get_file_json(language_code)
    final_translation = get_json_skeleton()

    keys_total = get_keys_total(final_translation, 0)

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
                    loading_bar.next()
                else:
                    target[key] = translate(val_t, language_code)
                    loading_bar.next()

    file_name = get_file_name(language_code)
    with Bar(f"({index}/{files_total}) {file_name}", suffix='%(percent)d%%', max=keys_total) as loading_bar:
        translate_object(existing_translation, final_translation)

    translated_json = json.dumps(final_translation, indent=4, ensure_ascii=False)
    return translated_json


def translate_files_in_dir(dir):
    language_codes = extract_language_codes_from_files(dir)
    languages_total = len(language_codes) - 1 # Number of langages to translate (minus source language)

    print(f"Found {languages_total} language files to translate in directory:")

    if from_language not in language_codes:
        exit_with_error(f"ERROR: Missing source language file: {from_language}.json")

    for index, language_code in enumerate(language_codes):
        if language_code != from_language:
            translation = translate_file(language_code, index, languages_total)
            save_file(translation, language_code)
    print("Translation complete!")

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
