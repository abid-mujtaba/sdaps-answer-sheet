"""
Extract the responses from the scanned in MCQ answer sheets.
"""

import csv
import sys


def main(raw_file, out_file, qid_file=None):

	# Read the qid_file and store the provided qids in a dictionary for later use
	Q = {}

	if qid_file:
		
		with open(qid_file, newline='') as fin:
			
			reader = csv.DictReader(fin)

			for row in reader:

				Q[int(row['q'])] = row['qid']

	

	with open(out_file, 'w', newline='') as fout:
		
		fieldnames = ['id', 'qid', 'rid']
		count = 0

		writer = csv.DictWriter(fout, fieldnames=fieldnames)
		writer.writeheader()

		with open(raw_file, newline='') as fin:

			reader = csv.DictReader(fin)
			# print(reader.fieldnames)

			for row in reader:		# 'row' is an OrderedDict containing the data in the csv row

				D = {}
				count += 1

				try:
					
					R = Row(count, row, Q)

					lten = [x for x in range(10)]		# List of the first ten digits

					# Construct Student Registration ID
					year = 10 * extract_single(count, row, '1_3', [0,1,2])
					year += extract_single(count, row, '1_4', lten)

					# Write extracted dictionary to output csv file
					writer.writerow(R.dict())
				
				except ValidationError as e:
					print("ValidationError: " + str(e))

				print(R.dict())
				# TODO Remove to iterate over all rows
				break

class Single:
	"""
	A data structure that is allowed to store only a single value (multiple pushes without intermediate pops are errors).

	It is intended for use in situations where the expected behaviour that ONLY ONE of a number of options is set.
	"""

	value = None

	def push(self, value):

		if self.value:
			raise self.PushException()

		self.value = value

	def pop(self):

		if not self.value:
			raise self.PopException()

		out = self.value
		self.value = None		# Empty out the held value since we have popped the value

		return out

	class PushException(Exception):
		"""
		Raised when push() is called with a value already present, not allowed in the 'Single' data structure by definition.
		"""
		pass
	
	class PopException(Exception):
		"""
		Raised when pop() is called with no value stored.
		"""
		pass


class Row:
	"""
	An object based on the input csv row which is capable of extracting information from the complicated structure of the sdaps csv output.
	"""

	def __init__(self, count, csv_row, qids):

		self.id = count
		self.row = csv_row
		self.qids = qids

		self.extract()


	def dict(self):
		"""
		Return the extracted information as a dicitonary.
		"""
		return self.D


	def extract(self):
		"""
		Extract the information from the csv row.
		"""

		D = {}
		row = self.row
		Q = self.qids

		D['id'] = self.id
		D['qid'] = row['questionnaire_id'][3:]		# Remove the 'FCI' substring at the start

		if row['questionnaire_id'] == 'None':

			if self.id in Q:

				D['qid'] = Q[self.id]

			else:
				raise ValidationError("Questionnaire ID is missing for row {}".format(count))

		# Now we pop the first two entries (questionnaire and global id)
		row.popitem(last=False)
		row.popitem(last=False)

		# We convert the remaining entries in to integers rather than strings for ease of processing (and boolean analysis)
		for key in row.keys():
			row[key] = int(row[key])

		semester = self.extract_semester()
		year = self.extract_year()

		D['rid'] = "BCS-{0}{1}-{2}".format(semester, year, 'XXX')

		self.D = D


	def extract_semester(self):
		"""
		Extract semester (FA/SP) in student id
		"""
		
		row = self.row

		sp = row['1_2_1_0']
		fa = row['1_2_2_0']

		if sp ^ fa:
			return 'SP' if sp else 'FA'
			
		else:
			raise ValidationError("Incorrect semester choice (FA/SP) in row: {}".format(self.id))


	def extract_year(self):
		"""
		Extract year in student id
		"""

		row = self.row
		year = ''

		S = Single()

		try:
			for i in range(1,4):

				if row["1_3_{}_0".format(i)]:
					
					S.push(i - 1)

			year += str(S.pop())			# Return the value stored (at one point) in the above loop

			for i in range(1,11):

				if row["1_4_{}_0".format(i)]:

					S.push(i - 1)

			year += str(S.pop())

		except S.PushException:
			raise ValidationError("Multiple checked boxes in Year Entry in row {}".format(self.id))

		except S.PopException:
			raise ValidationError("Missing checked boxes in Year Entry in row {}".format(self.id))

		return year



def extract_single(id, row, prefix, entries, checkZero = True):
	"""
	Extract an entry which appears singly in answer-sheet.tex (such as BEL/BPH or SP/FA).
	"""
	return extract(id, row, prefix, entries, checkZero, True)


def extract_group(id, row, prefix, entries, checkZero = True):
	"""
	Extract an entry which appears in a group such as A/B/C/D/E.
	"""
	return extract(id, row, prefix, entries, checkZero, False)


def extract(id, row, prefix, entries, checkZero = True, single = False):
	"""
	Extract the passed in row dictionary to check that at most one entry is filled.
	If checkZero is set we also confirm that at least one entry is filled.
	The prefix provides the common starting string of the entries (the remainder is generated based on the length of the list 'entries').

	The list entries maps the index to the actual value represented by the box e.g. 1/2 -> FA/SP
	"""

	fmt_str = "{prefix}_{index}_0" if single else "{prefix}_{index}"

	count = 0
	result = None

	for i in range(1, len(entries) + 1):

		# Construct the dictionary key to access the value in the dictionary
		key = fmt_str.format(prefix=prefix, index=i)

		if int(row[key]) != 0:
			count += 1
			result = entries[i - 1]
	
	if count > 1:
		raise ValidationError("More than one box is checked in Q. {prefix} in row {id}".format(id=id, prefix=prefix))

	if checkZero and count == 0:
		raise ValidationError("No box is checked in Q. {prefix} in row {id}".format(id=id, prefix=prefix))

	return result


class ValidationError(Exception):
	pass
			


if __name__ == '__main__':

	if len(sys.argv) == 3:
		
		main(sys.argv[1], sys.argv[2])

	elif len(sys.argv) == 4:

		main(sys.argv[1], sys.argv[2], sys.argv[3])
	
	else:
		print("Error - Correct command usage is: python3 extract-respones.py <raw csv> <output csv> [<qids csv>]")

