import asyncio
import json


def get_file():
    try:
        with open('results.txt', 'r', encoding='utf-8') as f:
            text = f.read()
            if text:
                information = json.loads(text)
                return information
            return {}
    except FileNotFoundError:
        open('results.txt', 'tw', encoding='utf-8')
        with open('results.txt', 'r', encoding='utf-8') as f:
            text = f.read()
            if text:
                information = json.loads(text)
                return information
            return {}


def put_file(final_dict):
    with open('results.txt', 'w', encoding='utf-8') as f:
        json.dump(final_dict, f)


class ClientServerProtocol(asyncio.Protocol):
    def __init__(self):
        super().__init__()
        self.transport = None
        self.wrong_command = 'error\nwrong command\n\n'

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        resp = self.process_data(data)
        self.transport.write(resp.encode('utf-8'))

    def process_data(self, result):
        req = result.decode('utf-8').strip()
        req = req.split(' ')
        comm = req[0]
        key = req[1]

        if comm == 'get':
            return self.get(key)
        elif comm == 'put':
            value = req[2]
            timestamp = req[3]
            return self.put(key, value, timestamp)
        else:
            return self.wrong_command

    def get(self, key):
        all_metrics = get_file()

        key_value = all_metrics.items()
        answer = 'ok\n'

        if key != '*':
            return self.all_information(key, all_metrics, answer)

        for keys, values in key_value:
            for val in values:
                answer = answer + keys +\
                         ' ' + val[1] +\
                         ' ' + val[0] +\
                         '\n'
        return answer + '\n'

    @staticmethod
    def put(key, value, timestamp):
        met = [timestamp, value]
        all_metrics = get_file()

        if key not in all_metrics:
            all_metrics[key] = [met]
            put_file(all_metrics)
        else:
            if met not in all_metrics[key]:
                all_metrics[key].append(met)
                all_metrics[key].sort(key=lambda x: x[0])
                put_file(all_metrics)
        return 'ok\n\n'

    @staticmethod
    def all_information(key, all_metrics, answer):
        if key in all_metrics:
            for value in all_metrics[key]:
                answer = answer + key +\
                         ' ' + value[1] +\
                         ' ' + value[0] +\
                         '\n'
        return answer + '\n'


def run_server(host, port):
    loop = asyncio.get_event_loop()
    coro = loop.create_server(ClientServerProtocol, host, port)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


def main():
    run_server('127.0.0.1', 8888)


if __name__ == '__main__':
    main()

