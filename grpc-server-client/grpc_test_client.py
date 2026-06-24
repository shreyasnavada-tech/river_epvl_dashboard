import grpc
import rideMetrics_pb2 as pb2
import rideMetrics_pb2_grpc as pb2_grpc


class fetchData:
    def __init__(self):
        self.channel = grpc.insecure_channel("localhost:50051")
        self.stub = pb2_grpc.RideMetricStub(self.channel)

    def pollTestStatus(self, test_data):
        request = pb2.testRequest(startTest=test_data)
        response = self.stub.pollTestStatus(request)
        return response


if __name__ == "__main__":
    a = fetchData()
    # The pollTestStatus values to be add
    # if testStatus -
    # 1. "START" - Start the thread and the test
    # 2. PAUSE" - Pauses the thread
    # 3. "RESUME" - Resumes the thread after an elapsed time
    # 4. "EXIT" - Calls join method on the thread
    print(a.pollTestStatus("EXIT"))
