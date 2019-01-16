with open('fatigue_volume_nodes_notched.inc', 'w') as inc_file:
    counter = 0
    file_string = ''
    for label in range(29321, 68520+1):
        file_string += str(label) + ', '
        counter += 1
        if counter == 16:
            inc_file.write(file_string[:-2] + '\n')
            counter = 0
            file_string = ''
