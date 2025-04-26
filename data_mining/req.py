import requests
import time
import datetime
import time
import dill as pickle
from tqdm import tqdm

def get_transactions_between_addresses(api_key, address1, address2, startblock=0, endblock=99999999):
    url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address1}&startblock={startblock}&endblock={endblock}&sort=asc&apikey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status() 
        data = response.json()

        if data["status"] == "1" and data["message"] == "OK":
            all_transactions = data["result"]
            transactions = [tx for tx in all_transactions if tx["to"].lower() == address2.lower() or tx["from"].lower() == address2.lower()]
            return transactions
        else:
            print(f"Error fetching transactions: {data['message']}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None

def get_first_and_last_transaction_times(api_key, address1, address2):
    transactions = get_transactions_between_addresses(api_key, address1, address2)

    if transactions is None or len(transactions) == 0:
        print("No transactions found between these addresses.")
        return None

    transactions.sort(key=lambda x: int(x["timeStamp"]))

    res = []
    for tx in transactions:
        res.append([datetime.datetime.fromtimestamp(int(tx["timeStamp"])), int(tx["value"]) / 10**18])

    return res

API_KEY = # YOUR_API_KEY_HERE
ADDRESS1 = "0x51e1b165acaa866d23609f7b5833e47d30b89820"
ADDRESS2 = "0x6c9a06a4e4910bdaf5de7fec580da6c87fe22f52"
GRAPH = 'ethereum_graph.gpickle'
output_filename = "save.txt"

if __name__ == "__main__":
    with open(GRAPH, 'rb') as f:
        graph = pickle.load(f)
    nodes = sorted(list(graph.nodes()))
    res = []
    ok = False
    for main_node in tqdm(nodes):
        label = graph.nodes[main_node]['original_label']
        for edge in tqdm(graph.edges(main_node)):
            for node in edge:
                if main_node == 209 and node == 668:
                    ok = True
                if node == main_node or node < main_node or not ok:
                    continue
                node_label = graph.nodes[node]['original_label']
                result = get_first_and_last_transaction_times(API_KEY, label, node_label)
                if result is not None:
                    res.append([main_node, node, result])
                    with open(output_filename, "a") as outfile:
                        for d in result:
                            line = f"{main_node},{node},{d[0]},{d[1]}\n"
                            outfile.write(line)
                time.sleep(0.25)

    with open("time_value.pickle", 'wb') as f:
        pickle.dump(res, f)
