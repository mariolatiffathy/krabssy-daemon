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
      
  - fabitimage_id: The ID of the FabitImage that is stored in the daemon database.
  
      Example: 123
      
      Required: yes
      
      Type: integer

## /api/v1/servers/<server_id>
**method**: GET

**description**: Retrives server information.

**notes**: The returned `is_online` is the status of the container, not the status of the processes of the container.

## /api/v1/servers/<server_id>
**method**: DELETE

**description**: Deletes a server

## /api/v1/servers/<server_id>/power
**method**: POST (in JSON)

**parameters**:

  - action: Either 'start', 'stop', or 'restart'
  
      Example: start
      
      Required: yes
      
      Type: string
      
## /api/v1/servers/<server_id>/console
**method**: POST (in JSON)

**parameters**:

  - command: The command to send to the server
  
      Example: say hi
      
      Required: yes
      
      Type: string
      
## /api/v1/servers/<server_id>/console
**method**: GET

**parameters**:

  - lines_limit: The limit of the console lines to output
  
      Example: 10
      
      Required: yes
      
      Type: integer