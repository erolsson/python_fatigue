with open('fatigue_volume_elements_smooth.inc', 'w') as inc_file:
    counter = 0
    file_string = ''
    for label in range(22461, 61660+1):
        file_string += str(label) + ', '
        counter += 1
        if counter == 16:
            inc_file.write(file_string[:-2] + '\n')
            counter = 0
            file_string = ''
