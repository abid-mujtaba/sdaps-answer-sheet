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

					print(R.dict())

					# Write extracted dictionary to output csv file
					writer.writerow(R.dict())
				
				except ValidationError as e:
					print("ValidationError: " + str(e))

				# TODO Remove to iterate over all rows
				# break


def range_1(n):
	"""
	Create a range object that starts at 1 and runs up to (and including) 'n'
	"""
	return range(1, n + 1)


class Single:
	"""
	A data structure that is allowed to store only a single value (multiple pushes without intermediate pops are errors).

	It is intended for use in situations where the expected behaviour that ONLY ONE of a number of options is set.
	"""

	value = None

	def __init__(self, prefix):
		"""
		Store the prefix of the object being traversed to help in debugging exceptions.
		"""
		self.prefix = prefix


	def push(self, value):

		if self.value is not None:						# Pushing with a value already present
			raise self.PushException(self.prefix)

		self.value = value

	def pop(self):

		if self.value is None:							# Popping when NO value is present
			raise self.PopException(self.prefix)

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


		try:
			S = Single("1_3")

			for i in range_1(3):

				if row["1_3_{}_0".format(i)]:
					
					S.push(i - 1)

			year += str(S.pop())			# Return the value stored (at one point) in the above loop


			S = Single("1_4")

			for i in range_1(10):

				if row["1_4_{}_0".format(i)]:

					S.push(i - 1)

			year += str(S.pop())

		except S.PushException as e:
			raise ValidationError("Multiple checked boxes in Year Entry in row {} (prefix {})".format(self.id, e))

		except S.PopException as e:
			raise ValidationError("Missing checked boxes in Year Entry in row {} (prefix {})".format(self.id, e))

		return year


class ValidationError(Exception):
	pass
			


if __name__ == '__main__':

	if len(sys.argv) == 3:
		
		main(sys.argv[1], sys.argv[2])

	elif len(sys.argv) == 4:

		main(sys.argv[1], sys.argv[2], sys.argv[3])
	
	else:
		print("Error - Correct command usage is: python3 extract-respones.py <raw csv> <output csv> [<qids csv>]")

