from optparse import OptionParser
from epubrepair import generate_data
from epubrepair import check_data

if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-t', '--test', dest='test', help='test target name')
	(options, args) = parser.parse_args()
	if options.test == 'generate-txt':
		print(generate_data('tmp', 'tmp', '生僻字目录', 'zh'))
	elif options.test == 'check-data':
		print(check('tmp'))