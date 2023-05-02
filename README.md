
# TCP-simulation-using-UDP
TCP is a reliable, connection-oriented protocol that ensures that data is transmitted in the correct order and without loss or duplication. UDP, on the other hand, is an unreliable, connectionless protocol that does not guarantee the delivery of data packets or their order.

In this project, We simulated TCP protocol using UDP by implementing reliable transmission such as 3-way-Handshaking for both initiating the connection and closing it and handling HTTP requests.

First of all you need to run both the server and client in separate terminal.
## Server
```bash
python Server.py
```
## Client
```bash
python Client.py
```
after running both in separate terminal, You will need to specify a HTTP method to use (POST or GET) for the client.

## Example
```python
GET /filename.txt
```
This will result in getting all the text from filename.txt by the server side and print it at the client side.

## Another Example
```python
post /filename.txt
```
this will result in sending the text for a buffer in the client side to the server side and saving it in a filename.txt (if filename.txt doesn't exist it will be automatically created).
You can add those text in the buffer by appending to a variable called data
```python
data.append("Saeed)
data.append("Hossam")
data.append("Ehab")
```
## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)