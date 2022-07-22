import sqlite3
from prettytable import from_db_cursor
from sqlite3 import Error
from passlib.hash import pbkdf2_sha256
from cryptography.fernet import Fernet
import getpass

DB_FILE = "password_manager.db"


class PasswordManager:
    def __init__(self) -> None:
        self.password_manager = "password_manager"
        self.master_password = "master_password"
        if not self.isSqlite3():
            self.createTables()
            self.createMasterPassword()

    def isSqlite3(self):
        from os.path import isfile

        if isfile(DB_FILE):
            return True
        return False

    def createMasterPassword(self):
        print(5 * "=" + " Create Master Password " + "=" * 5)
        user = input("[+] Enter username(Unique): ")
        master_pass1 = getpass.getpass("Enter password(Master): ")
        master_pass2 = getpass.getpass("Confirm password: ")
        if master_pass2 == master_pass1:
            self.generateMasterHash(user, master_pass1)
        else:
            print("opps.. please try again")
            self.createMasterPassword()

    def createConnection(self):
        """
        creating database connection with sqlite file
        you can use local host mysql or another database.
        """
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            return conn
        except Error as e:
            print(e)

        return conn

    def generateMasterHash(self, user, master_pass):

        try:
            conn = self.createConnection()
            sql_qury_master = f"insert into {self.master_password} (user_name,password,master_key) VALUES(?,?,?)"

            cursor = conn.cursor()
            # creating encrypted pass hash
            encrypted_hash = pbkdf2_sha256.hash(master_pass)
            key = Fernet.generate_key()
            insert_data = (user, encrypted_hash, key)
            cursor.execute(sql_qury_master, insert_data)
            conn.commit()
            print("[+] Master password hash is generated.")

        except Error as e:
            print(e)

    def createTables(self):
        """
        Creating mater password for password manager
        this is  the one time password for
        """
        sql_manager_table = f"CREATE TABLE IF NOT EXISTS {self.password_manager} (user_id INTEGER PRIMARY KEY AUTOINCREMENT,user_name varchar(50) UNIQUE,app_name varchar(100),pass_hash varchar(255), password varchar(255))"
        sql_master = f"CREATE TABLE IF NOT EXISTS {self.master_password} (user_name varchar(50) UNIQUE, password varchar(255),master_key varchar(255))"

        try:
            conn = self.createConnection()
            cursor = conn.cursor()
            cursor.execute(sql_manager_table)
            cursor.execute(sql_master)
        except Error as e:
            print(e)

    def insertData(self, data):
        """
        Insert data to the database with tuple parameter,
        like. username, app or website and password

        """
        conn = self.createConnection()
        sql = f"INSERT INTO {self.password_manager}(user_name,app_name,pass_hash,password) VALUES(?,?,?,?)"
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        print("[+] Data Inserted successfully.")

    def updateData(self, data):
        """
        update data to the database with tuple parameter,
        like. username, app or website and password

        while update data, you will be asked master password
        """
        conn = self.createConnection()
        sql = f"UPDATE {self.password_manager} SET user_name = ?, app_name = ?, password = ?,pass_hash =? WHERE password=? and user_name=?"

        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        print("Data successfully Updated")

    def displayAll(self, master_pass):
        _, master_hash, _ = self.getMasterPasswordHash()
        master = pbkdf2_sha256.verify(master_pass, master_hash)
        if master:
            conn = self.createConnection()
            try:
                with conn:
                    cur = conn.cursor()
                    cur.execute(
                        f"select user_id,user_name, app_name,pass_hash from {self.password_manager}"
                    )
                    x = from_db_cursor(cur)
                print(x)
            except Error as e:
                print(e)
            except IndexError as ie:
                return "Data Not found."

    def getMasterPasswordHash(self):
        """
        Retrieving master password hash from the table
        """
        conn = self.createConnection()
        cur = conn.cursor()
        cur.execute(f"select * from {self.master_password}")
        data = cur.fetchall()
        return data[0]

    def verifyPassword(self, master_pass):
        _, hash, _ = self.getMasterPasswordHash()
        result = pbkdf2_sha256.verify(master_pass, hash)
        return result

    def showPassword(self, data):
        conn = self.createConnection()
        with conn:
            cur = conn.cursor()
            cur.execute(
                f"select user_id,user_name, app_name,password from {self.password_manager} where user_name=? and app_name=?",
                data,
            )
            x = from_db_cursor(cur)
        print(x)


def main():
    psm = PasswordManager()

    while True:
        home_banner = """
        [============= Home Menu =============]

        [1] Manage Applications passwords
        [2] Update Master Password
        [0] Exit
        """
        app_banner = """
        [============= Application Menu =============]

        [1] Add password for Application or Website 
        [2] update Password
        [3] Show Password
        [4] Show all data
        [0] Exit
        """
        print(home_banner)
        choice = input("[+] Choice: ")
        # match case work only python >= 3.10
        match choice:
            case "0":
                print("\nBye....")
                break
            case "2":
                print("update master password")
                print("implement this by own")
            case "1":
                while True:
                    app_extension = "[App][+] "
                    print(app_banner)
                    choice2 = input(app_extension + "choice: ")
                    match choice2:
                        case "0":
                            print("[+] Application Menu Quit...")
                            break
                        case "1":
                            print(6 * "=" + " To Add data to the database " + "=" * 6)
                            user = input(app_extension + "Enter username: ")
                            app_name = input(
                                app_extension + "Enter (App name or Website): "
                            )
                            password = getpass.getpass(
                                app_extension + "Enter password: "
                            )
                            _, _, key = psm.getMasterPasswordHash()
                            f = Fernet(key)
                            encryped_hash = f.encrypt(bytes(password, "utf-8"))

                            data = (user, app_name, encryped_hash, password)
                            psm.insertData(data=data)

                        case "2":
                            print(6 * "=" + " To Update data " + "=" * 6)
                            master = getpass.getpass(
                                app_extension + "Enter password(Master): "
                            )
                            result = psm.verifyPassword(master)

                            if result:
                                print("please enter existing data first")
                                user = input("[+] Enter username(existing): ")
                                password = getpass.getpass(
                                    "[+] Enter password(existing web or app): "
                                )
                                print(6 * "=" + " Please Enter new data " + "=" * 6)

                                new_user = input("[+] Enter new username: ")
                                new_app_name = input(
                                    "[+] Enter new (App name or Website): "
                                )
                                new_password = getpass.getpass(
                                    "[+] Enter new password: "
                                )

                                _, _, key = psm.getMasterPasswordHash()
                                f = Fernet(key)
                                encryped_hash = f.encrypt(bytes(password, "utf-8"))

                                data = (
                                    new_user,
                                    new_app_name,
                                    new_password,
                                    encryped_hash,
                                    password,
                                    user,
                                )
                                psm.updateData(data)
                        case "3":
                            print(6 * "=" + " To Show Password " + "=" * 6)

                            user = input("[+] Enter username(existing): ")
                            app = input("[+] Enter (existing web or app): ")
                            data = (user, app)
                            psm.showPassword(data)
                        case "4":
                            master = getpass.getpass("[+] Enter password(Master): ")
                            psm.displayAll(master_pass=master)

                        case default:
                            return "[+] Invalid Choice!"

            case default:
                return


if __name__ == "__main__":
    main()
