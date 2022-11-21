import random


class Memory:
    def __init__(self, size_max, size_min):
        self.samples = []
        self.size_max = size_max
        self.size_min = size_min

    # Function which add a sample into memory
    def add_sample(self, sample):
        self.samples.append(sample)

        if len(self.samples) > self.size_max:
            self.samples.pop(0)  # if the length is greater than the size of memory, remove the oldest element
            print("Sample: ", self.samples)

    # Function which extracts n (batch size) samples from memory
    def get_samples(self, n):

        if len(self.samples) < self.size_min:
            return []

        if n > len(self.samples):
            return random.sample(self.samples, len(self.samples))  # get all the samples
        else:
            return random.sample(self.samples, n)  # get "batch size" number of samples
