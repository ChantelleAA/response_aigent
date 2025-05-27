**Steps to Download and Use VS Code with Python and Jupyter Notebook**

---

### 1. Install Visual Studio Code (VS Code)

* Go to: [https://code.visualstudio.com/](https://code.visualstudio.com/)
* Click the download button for your operating system.
* Run the downloaded installer.
* Follow the setup steps. Keep the default settings.
* Make sure "Add to PATH" and "Open with Code" are checked.
* Complete the installation.

---

### 2. Install Python

* Go to: [https://www.python.org/downloads/](https://www.python.org/downloads/)
* Click the download button for the latest Python version (e.g., Python 3.11).
* Run the downloaded installer.
* Check the box: “Add Python to PATH”.
* Click “Install Now”.
* After installation, open a terminal or command prompt and run:

  ```
  python --version
  ```

  You should see a version number.

---

### 3. Install Python Extension in VS Code

* Open VS Code.
* Click the Extensions icon on the left sidebar (or press `Ctrl+Shift+X`).
* Search for “Python”.
* Install the extension by Microsoft.

---

### 4. Install Jupyter Extension in VS Code

* In the Extensions panel, search for “Jupyter”.
* Install the extension by Microsoft.

---

### 5. Create a Project Folder

* In VS Code, click **File > Open Folder**.
* Create or select a folder for your Python projects.
* Click “Select Folder” to open it in VS Code.

---

### 6. Create and Use a Jupyter Notebook

* In VS Code, click **File > New File**.
* Save the file with a `.ipynb` extension (example: `project1.ipynb`).
* The Jupyter notebook interface will open.
* Add Python code in the cells.
* Press `Shift + Enter` to run a cell.

---

### 7. (Optional) Create and Use a Virtual Environment

* Open the terminal in VS Code (\`Ctrl + \`\` or View > Terminal).
* Run:

  ```
  python -m venv venv
  ```
* Activate the virtual environment:

  * Windows:

    ```
    venv\Scripts\activate
    ```
  * macOS/Linux:

    ```
    source venv/bin/activate
    ```
* Install Jupyter in the environment:

  ```
  pip install jupyter
  ```

---

### 8. Install Common Libraries (Optional)

You can install libraries like this:

```
pip install pandas matplotlib numpy
```
