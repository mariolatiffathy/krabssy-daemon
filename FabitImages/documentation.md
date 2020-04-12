# FabitImages Documentation
The FabitImages are files with the extension `.fabitimage` and are written in the JSON format.

A FabitImage lets you customize how you want a container to behave (i.e. what commands to execute on the server creation).

An example FabitImage can be found in this folder.

## FabitImages components
- name (string): The name of the FabitImage. This makes the FabitImage easy to identify. This name will be visible in the FabitManage Panel too.

- author (string): The author (creator) of the FabitImage.

- version (string): The version number of the FabitImage.

- events (object):
  - on_create (object): On server create event.
    - from_container (object): The commands to execute as the container user.
    - as_root (object): The commands to execute as the system owner.
    
## Notes
- The commands written in `as_root` are executed **after** the commands executed in `from_container`.

- The commands are executed in the same order that they are written in.

- The commands get executed in the container data path, for example `/home/fabitmanage/daemon-data/fabitmanage-Container1`.

## Samples
- Prevent user from deleting and modifying a file (***Exploital thinking:*** You must prevent the user from BOTH deleting AND modifying the file. Because if the user was able to delete the file, he/she can delete it and create it again and this way it will be modifyable):

```
"as_root": {
    "1": "chattr +u +i ./my_file.txt"         
}
```