__version__ = '1.0.1'

import random # Randomises integers.


# Character that delimits the data, as a side-effect it cannot be in any data files or user input.
DELIMITER = '|'

# Region input.

def get_input(prompt, check=lambda response: response, message='Invalid Input'):
	'''Get input from the user.

	Args:
		prompt - Message to prompt user with.
		check - Method that response must return Truthy from.
		message - Message to display if the check fails.

	Returns:
		str - Response of user.
	'''
	response = input(prompt).strip() # The input of the user is saved.

	# Asks the user to re-enter their response as long as the check fails or the DELIMITER string is within the response.
	while not check(response) or DELIMITER in response:
		if DELIMITER in response:
			print('"{}" is a forbidden character'.format(DELIMITER))
		else:
			print(message)
		response = input(prompt).strip()

	return response

def get_choice(*options): # This function makes the user make a choice between numbers.
	'''Get a choice from given options.

	Args:
		*options - Options the user may choose from.

	Returns:
		The chosen option, type depends on the option.
	'''
	# Prints out all the options with a numeric prefix.
	for i, option in enumerate(options):
		print('{}. {}'.format(i + 1, option))

	# Gets the choice as an int that is within the above printed numeric range.
	choice = int(get_input('> ', lambda choice: choice.isdigit() and int(choice) > 0 and int(choice) <= len(options), 'Invalid Choice'))
	print()

	return options[choice - 1]

#endregion

def register_user(usernames): # This function creates the username of the user.
	'''Register a user.

	Args:
		usernames - List of currently registered usernames.

	Returns:
		dict - User object.
	'''
	# Ensures username is Truthy and not used before.
	name = get_input('Name: ', lambda username: username and username not in usernames, 'Username already exists')
	password = get_input('Password: ')
	# Ensures age is a digit and greater then 0.
	age = get_input('Age: ', lambda age: age.isdigit() and int(age) > 0, 'Age must be a number greater then 0')
	year_group = get_input('Year Group: ')
	print()

	# Creates the username from the first three characters plus the age.
	username = '{}{}'.format(name[0:3], age)
	print('Your username is: {}\n'.format(username))

	return {
		'username': username,
		'password': password,
		'name': name,
		'age': age,
		'year_group': year_group
	}

def percentage_to_letter(percentage):
	'''Convert a percentage to a letter grade.

	Args:
		percentage - Percentage to convert.

	Returns:
		str - Letter representing the percentage.
	'''
	# Each tuple contains the minimum percentage the the letter
	# grade, and checking them in this order avoids having to
	# use five if branches.
	for part in [(90, 'A'), (80, 'B'), (70, 'C'), (60, 'D'), (0, 'F')]:
		if percentage >= part[0]:
			return part[1]

	return None

def take_quiz(difficulty, questions): # This function is used when the user is taking the quiz.
	'''Take a quiz.

	Args:
		difficulty - Difficulty to take quiz at.
		questions - List of question dicts to ask.

	Returns:
		int - Percentage of questions gotten correct.
	'''
	# A one-line way to convert the three difficulties to numbers.
	# Represents how many questions each is worth.
	question_count = 2 if difficulty == 'Easy' else 3 if difficulty == 'Medium' else 4 if difficulty == 'Hard' else 0

	correct = 0
	for question in questions:
		print('Question: {}'.format(question['question']))

		# Collects the options and shuffles them.
		options = [question['correct']] + question['incorrect'][0:question_count - 1]
		random.shuffle(options)

		answer = get_choice(*options)
		if answer == question['correct']:
			print('Correct!')
			correct += 1
		else:
			print('Incorrect! The answer was: {}'.format(question['correct']))

	percentage = correct / len(questions) * 100
	letter = percentage_to_letter(percentage)

	print('Result: {}/{} - {}% - {}'.format(correct, len(questions), percentage, letter))

	return percentage

def choose_category_and_difficulty(quizzes): # This functions choses the category and the difficulty of the quiz.
	'''Get the user choice for category and difficulty.

	Args:
		quizzes - Dictionary of quiz categories.

	Returns:
		tuple - A two part tuple, containins the category and difficulty chosen, may be none if there are no available categories.
	'''
	if not quizzes:
		print('No Categories')
		return None, None

	# Enforces order for the category names by sorting them.
	print('Category:')
	category = get_choice(*sorted(list(quizzes.keys())))

	print('Difficulty:')
	difficulty = get_choice('Easy', 'Medium', 'Hard')

	return category, difficulty

#region Menus

def login_menu(users, quizzes, results): # This function is used during the login menu phase.
	'''Attempt to login a user.

	Args:
		users - List of users.
		quizzes - Dictionary of quizzes.
		results - List of previous results.
	'''
	username = get_input('Username: ') # The input of the user is saved as the username and it displays it to the menu.
	password = get_input('Password: ') # The input of the user is saved as the password and it displays it to the menu.

	# Loops through all users, and if it finds one whom the provided credentials match, it enters the user menu as them.
	for user in users:
		if user['username'] == username and user['password'] == password:
			user_menu(users, quizzes, results, user)
			return

	print('Invalid Username/Password') 

def user_menu(users, quizzes, results, user):
	'''Provice the user options.

	Args:
		users - List of users.
		quizzes - Dictionary of quizzes.
		results - List of previous results.
		user - Currently logged-in user.
	'''
	print('Hello {}'.format(user['username']))

	choice = get_choice('Take Quiz', 'Return to Main Menu') # Makes the user choose between Take Quiz and Return to Main Menu.
	if choice == 'Take Quiz':
		category, difficulty = choose_category_and_difficulty(quizzes)
		if category is None:
			return

		# At this point a quiz must be taken, so it creates the result it objects and saves it.
		results.append({
			'category': category,
			'username': user['username'],
			'difficulty': difficulty,
			'percentage': take_quiz(difficulty, quizzes[category])
		})
		save_results(results)
	elif choice == 'Return to Main Menu':
		return
	else:
		raise NotImplementedError()

	user_menu(users, quizzes, results, user)

def report_menu(users, quizzes, results): # This function is used during the report menu phase.
	'''View a report.

	Args:
		users - List of users.
		quizzes - Dictionary of quizzes.
		results - List of previous results.
	'''
	print('Report Type:')
	choice = get_choice('User', 'Quiz')
	if choice == 'User':
		if not users:
			print('No Users')
			return

		print('Choose Username:')
		username = get_choice(*[user['username'] for user in users])

		# Loops over results that were taken by the chosen username.
		print('User Results')
		for result in [result for result in results if result['username'] == username]:
			# Uses named variables when formatting as most are within the result object already.
			print('{letter} {percentage}% - {category}, {difficulty}'.format(letter=percentage_to_letter(result['percentage']), **result))

		print()
	elif choice == 'Quiz':
		category, difficulty = choose_category_and_difficulty(quizzes)
		if category is None:
			return

		average, count, highest = 0, 0, [0, None]
		# Loops over results that match the category and difficulty chosen.
		for result in [result for result in results if result['category'] == category and result['difficulty'] == difficulty]:
			average += result['percentage']
			count += 1
			if result['percentage'] > highest[0]:
				highest = [result['percentage'], result['username']]

		# Prevents diving by zero.
		if average != 0 and count != 0:
			average /= count

		# Converts the username of highest[1] to a user object.
		for user in users:
			if user['username'] == highest[1]:
				highest[1] = user
				break

		print('Average : {}\nHighest : {}%\n'.format(average, highest[0]))

		if highest[1]:
			print('Username   : {username}\nName       : {name}\nAge        : {age}\nYear Group : {year_group}'.format(**highest[1]))

		print()
	else:
		raise NotImplementedError()

def main_menu(users, quizzes, results):
	'''Main menu from which everything else can be accessed.

	Args:
		users - List of users.
		quizzes - Dictionary of quizzes.
		results - List of previous results.
	'''
	choice = get_choice('Register', 'Login', 'Report', 'Exit')
	if choice == 'Register':
		new_user = register_user([user['username'] for user in users])

		# Saves the new user.
		users.append(new_user)
		save_users(users)

		# Automatically logs in as the newly registered user.
		user_menu(users, quizzes, results, new_user)
	elif choice == 'Login':
		login_menu(users, quizzes, results)
	elif choice == 'Report':
		report_menu(users, quizzes, results)
	elif choice == 'Exit':
		exit()
	else:
		raise NotImplementedError()

	main_menu(users, quizzes, results)

#endregion

#region Data

def load_quizzes(filepath='quizzes.txt'): # This function loads up the quizes from the text file.
	'''Load quizzes from text file.

	Args:
		filepath - Filepath of text file to load from.

	Yields:
		tuple - Category name and list of quizzes that belong to category.
	'''
	with open(filepath, 'r') as file: # Opens the text file called quizzes.
		category = None
		quizzes = []
		for line in [line.strip() for line in file.readlines()]:
			# If the line has text and the category is none, then it must be the category name.
			if line and category is None:
				category = line
				continue

			# If the line has text but the category has already been set, it must be a quiz.
			if line and category is not None:
				parts = line.split(DELIMITER)
				quizzes.append({
					'question': parts[0],
					'correct': parts[1],
					'incorrect': parts[2:]
				})
				continue

			# If the line is blank but the category has been set ...
			# and there are quizzes, then there will be no more quizzes ...
			# so yield the data and reset the variables.
			if not line and category and quizzes:
				yield category, quizzes
				category = None
				quizzes = []

		# If there was no newline at the end of the file but ...
		# there is leftover data, yield it.
		if category and quizzes:
			yield category, quizzes

def save_data(filepath, data, *fieldnames): # Saves data to the file.
	'''Save data to a filepath with ordered fieldnames.

	Args:
		filepath - Filepath to save data to.
		data - List of dicts to save.
		*fieldnames - Names of fields to save dict data, in order.
	'''
	with open(filepath, 'w') as file:
		for item in data:
			# Creates formatting-strings for the data, for example:
			#
			# >>> save_data(..., ..., 'bravo', 'alpha', 'charlie')
			# line = {bravo}|{alpha}|{charlie}
			#
			# and then line can be formatted with the values of item.
			line = '{{{}}}\n'.format('}|{'.join(fieldnames)).format(**item)
			file.write(line)

def load_users(filepath='users.txt'): # Loads the users from a text file.
	'''Load the users from a file.

	Args:
		filepath - Filepath to load users from.

	Yields:
		dict - User objects.
	'''
	with open(filepath, 'r') as file: # Opens the file.
		for line in [line.strip() for line in file.readlines()]:
			if not line:
				continue

			# Zips up fieldnames and values and converts the age to an int.
			user = dict(zip(['username', 'password', 'name', 'age', 'year_group'], line.split(DELIMITER)))
			user['age'] = int(user['age'])
			yield user

def save_users(users, filepath='users.txt'): # Saves the users to the text file.
	'''Save the users to a file.

	Args:
		users - List of user dicts to save.
		filepath - Filepath to save users to.
	'''
	save_data(filepath, users, 'username', 'password', 'name', 'age', 'year_group')

def load_results(filepath='results.txt'): # Loads up the quiz results from the text file.
	'''Load quiz results from file.

	Args:
		filepath - Filepath to load results from.

	Yields:
		dict - Result objects
	'''
	with open(filepath, 'r') as file:
		for line in [line.strip() for line in file.readlines()]:
			if not line:
				continue

			# Zip up fieldnames and values, and convert percentage to float.
			result = dict(zip(['username', 'category', 'difficulty', 'percentage'], line.split(DELIMITER)))
			result['percentage'] = float(result['percentage'])
			yield result

def save_results(results, filepath='results.txt'): # Saves the quiz results to the text file.
	'''Save the results to a file.

	Args:
		results - List of quiz results to save.
		filepath - Filepath to save results to.
	'''
	save_data(filepath, results, 'username', 'category', 'difficulty', 'percentage')


#endregion

if __name__ == '__main__':
	# Tries to load the users, quizzes, results, and starts the main menu.
	try:
		users = list(load_users())
	except:
		print('Unable to load Users...')
		users = []

	try:
		quizzes = dict(load_quizzes())
	except:
		print('Unable to load Quizzes...')
		quizzes = {}

	try:
		results = list(load_results())
	except:
		print('Unable to load Results...')
		results = []

	main_menu(users, quizzes, results)

# End of code.
# https://pastebin.com/QUS4vXb4
# Code is 442 lines long.

