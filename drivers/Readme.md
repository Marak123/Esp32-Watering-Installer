# Sterowniki do ESP32 na Windows

***

### 1. `CP210x_Universal_Windows_Driver-File.zip `
#### Zawiera same sterowniki (pliki) bez instalatora


aby zainstalowaćsterowniki należy przejść do `Menedżer urządzeń`
i wybrać płytkę ESP32 która jest w folderze `Inne urządzenia`


![Menedżer urządzeń](./image/inne-not-install.png?raw=true "Employee Data title")

Przejdż do właściwości płytki i wybierz `Aktualizuj sterownik...`


![Menedżer urządzeń](./image/update-window.png?raw=true "Employee Data title")

Kliknij `Przeglądaj mój komputer w poszukiwaniu sterowników`


![Menedżer urządzeń](./image/search-window.png?raw=true "Employee Data title")

Kliknij `Przeglądaj...` i wybierz likalizację rozpakowanego archiwum `CP210x_Universal_Windows_Driver-File.zip`


![Menedżer urządzeń](./image/file-set.png?raw=true "Employee Data title")

##### Poprawnie wykonane powyższe czynnośći powinny zainstalować sterowniki do ESP32


***

### 2. `CP210x_Windows_Drivers-Installer.zip `
##### Zawiera sterowniki wraz z instalatorem (plikiem .exe)

Instalacja w tym przypadku jest bardzo prosta.

Po rozpakowaniu archiwum należy wybrać plik `CP210xVCPInstaller_x64.exe` lub `CP210xVCPInstaller_x86.exe` zależnie od wersji bitowej zainstalowanego systemu operacyjnego.
