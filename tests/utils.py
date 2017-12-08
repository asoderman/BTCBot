def assert_in_list(element, l):
	for e in l:
		if element.name == e.name:
			return True

	raise AssertionError('Element does not exist in list. {}'.format(element))