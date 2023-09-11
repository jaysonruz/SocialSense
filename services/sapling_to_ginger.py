def sapling_to_gingerit_format(sapling_response, original_text):
    print(f"original text:  {original_text} {len(original_text)}")
    corrected_text = original_text

    corrections = []
    offset = 0  # Initialize an offset to track cumulative position shifts

    for correction in sapling_response:
        start = correction['start'] + offset  # Adjust start position based on cumulative offset
        end = correction['end'] + offset  # Adjust end position based on cumulative offset
        replacement = correction['replacement']
        general_error_type = correction['general_error_type']

        # Calculate the length difference between the replaced text and the replacement
        length_diff = len(replacement) - (end - start)

        # Apply the correction to the text
        corrected_text = corrected_text[:start] + replacement + corrected_text[end:]
        print(f"""after correction :  {corrected_text} \n
              length of word to be replaced: {end - start} \n
              length of replacement: {len(replacement)} \n
              corrected result: {corrected_text}""")

        # Update the offset based on the length difference
        offset += length_diff

        # Create the correction object
        correction_obj = {
            "start": start,
            "text": original_text[start:end],
            "correct": replacement,
            "definition": general_error_type
        }

        corrections.append(correction_obj)

    # Create the desired output format
    output = {
        "text": original_text,
        "result": corrected_text,  # Use the corrected_text here
        "corrections": corrections
    }

    return output

if __name__ == "__main__":
    # Example usage:
    sapling_response = [{'end': 30,
                        'error_type': 'R:SPELL',
                        'general_error_type': 'Spelling',
                        'id': 'd30cf318-e1d5-5193-b90a-b596e5008e3d',
                        'replacement': 'kingdom come, this',
                        'sentence': 'this is my kimgdom come , thsi is my kindom cum.',
                        'sentence_start': 0,
                        'start': 11},
                        {'end': 43,
                        'error_type': 'R:SPELL',
                        'general_error_type': 'Spelling',
                        'id': '006e1f27-c52e-5f7b-b5c4-21c187f6d131',
                        'replacement': 'kingdom',
                        'sentence': 'this is my kimgdom come , thsi is my kindom cum.',
                        'sentence_start': 0,
                        'start': 37}]

    original_text = "this is my kimgdom come , thsi is my kindom cum."

    gingerit_output = sapling_to_gingerit_format(sapling_response, original_text)
    print(gingerit_output)
