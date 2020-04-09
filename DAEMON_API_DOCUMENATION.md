## /api/v1/servers/create
**method**: POST (in JSON)

**parameters**:
  - allowed_ports: The allowed port(s) seperated by commas.
      Example: 25565,25566
      Example: 25565
      Required: yes
      Type: string
  
   - server_id: An identifier so the panel can identify the newly created server in the future.
      Example: 123
      Example: abc
      Required: yes
      Type: string
      
  - enable_ftp: Should the server have FTP enabled or no.
      Example: true
      Example: false
      Required: yes
      Type: boolean
      
  - ram: The RAM of the server in MBs, minimum is 32 MB.
      Example: 512
      Required: yes
      Type: integer
      
  - cpu: The CPU of the server, 100 = 1 CPU core.
      Example: 50 (0.5 cores)
      Required: yes
      Type: integer
      
  - disk: The diskspace of the server in MBs, minimum is 3 MB.
      Example: 1024
      Required: yes
      Type: integer
      
  - startup_command: The startup command of the server.
      Example: java -jar mc.jar
      Required: yes
      Type: string