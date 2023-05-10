import socket
import subprocess
import threading
import psutil


def scan_port(port):
    sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockt.settimeout(4)
    result = sockt.connect_ex((target, port))
    if result == 0:
        print('[+] Port ' + str(port) + ' is open.')
        # Determine service type and version using nmap
        try:
            output = subprocess.check_output(['nmap', '-sV', '-p', str(port), '--open', target])
            output_str = output.decode('utf-8')
            service_info = output_str.split('\n')[2].strip()
            print('[+] Service type and version:', service_info)
        except Exception as e:
            pass

        # Determine service name using netstat and psutil
        try:
            output = subprocess.check_output(['netstat', '-aon'])
            output_str = output.decode('utf-8')
            for line in output_str.split('\n')[3:]:
                if line.strip() == '':
                    continue
                _, _, _, _, _, _, pid = line.split()
                if int(pid) == 0:
                    continue
                process_name = psutil.Process(int(pid)).name()
                print('[+] Service name:', process_name)
        except Exception as e:
            pass

    sockt.close()


target = input('Enter IP: ')
try:
    port = input('Enter 1 (ports 1-1000) 2 (all ports): ')
    if port == "exit":
        print("See you soon!")
    elif port == "1":
        print('Scanning ports 1-1000...')
        open_ports = []
        threads = []
        for x in range(1, 1001):
            t = threading.Thread(target=scan_port, args=(x,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
    elif port == "2":
        print('Scanning all ports...')
        open_ports = []
        threads = []
        for x in range(1, 65536):
            t = threading.Thread(target=scan_port, args=(x,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
    else:
        sockt = socket.socket()
        sockt.connect((target, int(port)))
        sockt.send('GET / HTTP/1.1\r\nHost: {}\r\n\r\n'.format(target).encode())
        socket.setdefaulttimeout(4)
        response = sockt.recv(2048).decode()
        server_header = response.split('\r\n')[0]
        print('[+] The service type and version is ' + server_header + 'and port:', port)
        sockt.close()
except ValueError:
    print('Invalid input.')
