"""
CSC148, Winter 2025
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2025 Bogdan Simion, Diane Horton, Jacqueline Smith
"""
import time
import datetime
from call import Call
from customer import Customer
from typing import Optional


class Filter:
    """ A class for filtering customer data on some criterion. A filter is
    applied to a set of calls.

    This is an abstract class. Only subclasses should be instantiated.
    """
    def __init__(self) -> None:
        pass

    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Return a list of all calls from <data>, which match the filter
        specified in <filter_string>.

        The <filter_string> is provided by the user through the visual prompt,
        after selecting this filter.
        The <customers> is a list of all customers from the input dataset.

         If the filter has
        no effect or the <filter_string> is invalid then return the same calls
        from the <data> input.

        Note that the order of the output matters, and the output of a filter
        should have calls ordered in the same manner as they were given, except
        for calls which have been removed.

        Precondition:
        - <customers> contains the list of all customers from the input dataset
        - all calls included in <data> are valid calls from the input dataset
        """
        raise NotImplementedError

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        raise NotImplementedError


class ResetFilter(Filter):
    """
    A class for resetting all previously applied filters, if any.
    """
    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Reset all of the applied filters. Return a List containing all the
        calls corresponding to <customers>.
        The <data> and <filter_string> arguments for this type of filter are
        ignored.

        Precondition:
        - <customers> contains the list of all customers from the input dataset
        """
        filtered_calls = []
        for c in customers:
            customer_history = c.get_history()
            # only take outgoing calls, we don't want to include calls twice
            filtered_calls.extend(customer_history[0])
        return filtered_calls

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Reset all of the filters applied so far, if any"


class CustomerFilter(Filter):
    """
    A class for selecting only the calls from a given customer.
    """
    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Return a list of all unique calls from <data> made or
        received by the customer with the id specified in <filter_string>.

        The <customers> list contains all customers from the input dataset.

        The filter string is valid if and only if it contains a valid
        customer ID.
        - If the filter string is invalid, return the original list <data>
        - If the filter string is invalid, your code must not crash, as
        specified in the handout.

        Do not mutate any of the function arguments!
        """
        filtered_calls = []
        filtered_digits = ''.join(filter(str.isdigit, filter_string)) # str
        filtered_cus = None
        for customer in customers: 
            customer_id = str(customer.get_id())
            if customer_id in filtered_digits: 
                filtered_cus = customer
                break 
        if filtered_cus is None: 
            return data 
        phone_numbers = filtered_cus.get_phone_numbers()
        for call in data: 
            if (call.dst_number in phone_numbers or call.src_number in phone_numbers) and (call not in filtered_calls): 
                filtered_calls.append(call)
        return filtered_calls           
        
    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Filter events based on customer ID"


class DurationFilter(Filter):
    """
    A class for selecting only the calls lasting either over or under a
    specified duration.
    """
    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Return a list of all unique calls from <data> with a duration
        of under or over the time indicated in the <filter_string>.

        The <customers> list contains all customers from the input dataset.

        The filter string is valid if and only if it contains the following
        input format: either "Lxxx" or "Gxxx", indicating to filter calls less
        than xxx or greater than xxx seconds, respectively.
        - If the filter string is invalid, return the original list <data>
        - If the filter string is invalid, your code must not crash, as
        specified in the handout.

        Do not mutate any of the function arguments!
        """
        filtered_calls = []
        def get_digits(s: str) -> str: 
            # this fn handle getting at least one and at most 3 digits 
            result = ""
            for i in range(3): 
                if s[i].isdigit(): 
                    result += s[i]
                else: 
                    break 
            try: 
                return int(result)
            except: 
                return None
            
        match = False
        for index, char in enumerate(filter_string): 
            if char == "G": 
                try:
                    potential = get_digits(filter_string[index+1:])
                    if potential is not None and match == False: 
                        match = True 
                        for call in data: 
                            if call.duration > potential and call not in filtered_calls: 
                                filtered_calls.append(call)
                except: 
                    return data 
            if char == "L": 
                try: 
                    potential = get_digits(filter_string[index+1:])
                    if potential is not None and match == False: 
                        match = True 
                        for call in data: 
                            if call.duration < potential and call not in filtered_calls: 
                                filtered_calls.append(call)
                except: 
                    return data  
        if match: 
            return filtered_calls
        else: 
            return data 

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Filter calls based on duration; " \
               "L### returns calls less than specified length, G### for greater"


class LocationFilter(Filter):
    """
    A class for selecting only the calls that took place within a specific area
    """
    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Return a list of all unique calls from <data>, which took
        place within a location specified by the <filter_string>
        (at least the source or the destination of the event was
        in the range of coordinates from the <filter_string>).

        The <customers> list contains all customers from the input dataset.

        The filter string is valid if and only if it contains four valid
        coordinates within the map boundaries.
        These coordinates represent the location of the lower left corner
        and the upper right corner of the search location rectangle,
        as 2 pairs of longitude/latitude coordinates, each separated by
        a comma and a space:
          lowerLong, lowerLat, upperLong, upperLat
        Calls that fall exactly on the boundary of this rectangle are
        considered a match as well.
        - If the filter string is invalid, return the original list <data>
        - If the filter string is invalid, your code must not crash, as
        specified in the handout.

        Do not mutate any of the function arguments!
        """
        filtered_calls = []
        def is_valid(s: str, type: str) -> Optional[bool|int]: 
            # precondition: s[0] starts with a digit or (-). This function finds the longest valid float number starting at index 0. 
            # Then, it will check if the float number is within the acceptable lon or lat range
            result = ""
            allow_period = True
            # find a valid number 
            for index, char in enumerate(s):
                if char.isdigit():
                    result += char
                elif index == 0 and char == "-":
                    result += char
                elif char == "." and allow_period == True:
                    result += char
                    allow_period = False
                else:
                    break
            # check if it's within the lon or lat range 
            try:
                length = len(result)
                result = float(result)
                if type == "lon":
                    if -180 <= result <= 180:
                        type = "lat"
                        return result, type, length
                if type == "lat":
                    if -90 <= result <= 90:
                        type = "lon"
                        return result, type, length
            except:
                return False, type, 0
            return False, type, 0
        
        def get_starting_point(s: str, prefix: bool) -> str:
            # return a mutated str with the starting point being a digit or a (-)
            for index, char in enumerate(s):
                try:
                    if s[index] == "," and s[index + 1] == " " and prefix == False:
                        return s[index+2:]
                    elif (char == "-" or char.isdigit()) and prefix == True:
                        return s[index:]
                except:
                    continue
            return ""
        result = []
        new_filter_string = get_starting_point(filter_string, prefix=True)
        potential, type, length = is_valid(new_filter_string, type="lon")
        if potential is not False:
            result.append(potential)
        new_filter_string = new_filter_string[length:]
        
        while (len(result) != 4) and (len(new_filter_string) != 0):
            new_filter_string = get_starting_point(new_filter_string, prefix=False)
            potential, type, length = is_valid(new_filter_string, type)
            if potential is not False:
                result.append(potential)
            new_filter_string = new_filter_string[length:]

        if len(result) != 4:
            return data
        
        for call in data: 
            if (result[0] <= call.src_loc[0] <= result[2]) and (result[1] <= call.src_loc[1] <= result[3]) and (call not in filtered_calls): 
                filtered_calls.append(call)
            if (result[0] <= call.dst_loc[0] <= result[2]) and (result[1] <= call.dst_loc[1] <= result[3]) and (call not in filtered_calls): 
                filtered_calls.append(call)
        return filtered_calls
            


    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Filter calls made or received in a given rectangular area. " \
               "Format: \"lowerLong, lowerLat, " \
               "upperLong, upperLat\" (e.g., -79.6, 43.6, -79.3, 43.7)"

if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'time', 'datetime', 'call', 'customer'
        ],
        'max-nested-blocks': 4,
        'allowed-io': ['apply', '__str__'],
        'disable': ['W0611', 'W0703'],
        'generated-members': 'pygame.*'
    })
    
