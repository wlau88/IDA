from abc import ABCMeta, abstractmethod
import pickle

class BaseMetadata(object):
    """Abstract class for api interaction for metadata

    Parameters:
    -----------
    """
    __metaclass__ = ABCMeta

    def to_pickle(data, fname):
        """Dumps data to pickle object at the provided 
        file path

        :param data: data to be pickled
        :param fname: file path of data to be pickled
        :return:
        """
        cwd = os.path.dirname(__file__) #gets current directory

        fname_path = os.path.join(cwd, 'pickles', fname)
        
        #check for validity of path input
        if not os.path.exists(fname_path):
            err_msg = '%s does not exist!' % fname_path
            err_msg.format(fname_path)
            raise IOerror(err_msg)

        with open(fname_path, 'w') as f:
            pickle.dump(data, f)


    def from_pickle(fname):
        """Loads data from pickle object at the provided
        file path

        :param fname: file path of the pickled data
        :return: pickled object
        """
        cwd = os.path.dirname(__file__) #gets current directory

        fname_path = os.path.join(cwd, 'pickles', fname)
        
        #check for validity of path input
        if not os.path.exists(fname_path):
            err_msg = '%s does not exist!' % fname_path
            err_msg.format(fname_path)
            raise IOerror(err_msg)

        with open(fname_path, 'r') as f:
            return pickle.load(f)