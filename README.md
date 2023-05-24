# Task Management App

This is a simple task management app built using Python and Streamlit.

## Installation

1. Clone the repository:

```
git clone https://github.com/abhishekaryan23/Task_Master.git
```

2. Set up a virtual environment and activate it

```
python -m venv env
source env/bin/activate (Linux/MacOS) 
env\Scripts\activate (Windows)
```

3. Install the dependencies:

```
pip install -r requirements.txt
```
4. Set up your MongoDB connection string:

* If you're running the app locally, create a `config.toml` file in the src directory of the project and add the following:

  ```
  [mongodb]
  uri = "your-mongodb-connection-string"
  ```

  Replace `"your-mongodb-connection-string"` with your actual MongoDB connection string.

* If you're hosting the app in Streamlit Sharing, add a secret for your MongoDB connection string in the "Settings" tab of your Streamlit app.

5. Start the app:


```
streamlit run app.py
```

## Features

- User and admin authentication
- Create and manage users
- Create and assign tasks
- Monitor task progress
- Update task status
- Filter tasks by status, Users, priority
- added task dependecy.
- added task statistics visualization.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the [MIT License](LICENSE).
