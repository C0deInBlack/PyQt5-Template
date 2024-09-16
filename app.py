#! /usr/bin/env python3

# Version: 2.3

import shutil, sys, os, copy
import pypdfium2
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QAction, QMessageBox, QFileDialog, QLineEdit, QInputDialog
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt


# ================================================== Default configuration to show a PDF ==================================================================


global file_path
global favorites; favorites = ''
global image_paths; image_paths = []
global activate_favorites; activate_favorites = False
global count_; count_ = 0
global employee_number; employee_number = ''
global default_number; default_number = True
global employee_number_path
global color_; color_ = '#00aaff'
global border; border = 5
global bg_color; bg_color = 'black'
global font_; font_ = 'Roboto'
global images_copy, favorites_copy
global favorite_on, favorite_off, button_style, messageBox_style

messageBox_style = f"""
                    background-color: {bg_color};
                    color: {color_};
                    """

try:
    for i in ['images', 'temporal_images', 'pdf', 'favorites', 'users']:  # Create the folder to save the images, the temporal images and the pdfs
        try: os.makedirs(os.path.join('assets', i))
        except: pass
except: pass

try:
    file_path = open('assets/default.txt', 'r') # Text file where is saved the default pdf path
    pdf_path = file_path.read()
    
    file_name = os.path.basename(pdf_path).split('.')[0]    # Get the filename without extension

    favorites = file_name
    
    try:
        new_pdf_folder = os.path.join('assets/images', file_name) # Create a folder with the file name
        os.makedirs(new_pdf_folder)
    except FileExistsError: pass


    pdf = pypdfium2.PdfDocument(pdf_path)
    for page_number in range(len(pdf)):
        page = pdf.get_page(page_number)
        pil_image = page.render(scale=300/72).to_pil()
        pil_image.save(f'assets/images/{file_name}_{page_number}.png')

    list_ = sorted(f'assets/images/{file_name}/{text}' for text in os.listdir(f'assets/images/{file_name}/'))
    image_paths = sorted(list_, key=lambda x : int(x.split('_')[-1].split('.')[0]))

    global images_copy; images_copy = image_paths
    global favorites_copy; favorites_copy = favorites
    
    file_path.close()
except FileNotFoundError: pass


# =============================================================== Main Window =========================================================================


class JobInstructionPDF(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initGUI()


# ===================================================== Functions for 'Help menu' =========================================================================
    

    def show_info(self):
        """ Simple message box, show information about the auhtor and the project
        """

        msg_info = QMessageBox() # Declare as MessageBox
        msg_info.setIcon(QMessageBox.Information) # Set the type of MessageBox
        # Text inside the MessageBox
        msg_info.setText("PyQt5 Template\nVersion: 2.3\n")
        msg_info.setWindowTitle('About')    # Set the title of the window
        msg_info.setFont(QFont(f'{font_}', 11))
        msg_info.setStyleSheet(messageBox_style)
        retval = msg_info.exec_()   # Execute the MessageBox window


    def show_license(self):
        """ Message box, show the license of this project
        """

        msg_license = QMessageBox() # Declare as MessageBox
        msg_license.setIcon(QMessageBox.Information)    # Set the type of MessageBox
        msg_license.setText("License goes here")
        msg_license.setWindowTitle('License')   # Set the title of the window
        msg_license.setStyleSheet(messageBox_style)
        msg_license.setFont(QFont(f'{font_}', 11))
        retval = msg_license.exec_()    # Execute the MessageBox window


    def suggest_message(self):
        """ Show this message box if the user haven't set a deafault pdf
        """

        msg_info = QMessageBox()    # Declare as MessageBox
        msg_info.setIcon(QMessageBox.Information)   # Set the type of MessageBox
        msg_info.setText("Welcome\nPlease add a PDF file as a default, you can do it in 'options'\nAlso you can only open or save a PDF")
        msg_info.setWindowTitle('Welcome')  # Set the window title
        msg_info.setStyleSheet(messageBox_style)
        msg_info.setFont(QFont(f'{font_}', 11))
        retval = msg_info.exec_()


# ============================================================= Save the pdf into images ==============================================================


    def save_pdf_image(self, path, dest, filename):
        """ This funtion converts a pdf in png images
        Args:
            path (str): Is the path of the pdf
            dest (str): The destination path where we want to save the images
            filename (str): The name of each image
        """

        pdf = pypdfium2.PdfDocument(path)
        for page_number in range(len(pdf)):
            page = pdf.get_page(page_number)
            pil_image = page.render(scale=300/72).to_pil()
            pil_image.save(f'{dest}/{filename}_{page_number}.png')


# ================================================== Principal function to show the PDF =================================================================


    def show_image(self, page):
        """ Show the image, image_paths is list where the are saved
            the path of the image, each saved pdf has it own list and folder
        
        Args:
            page (int): Is the element of the list, the image that we want
            to show, this function will be called with de argument
            self.image_index
        """

        pixmap = QPixmap(image_paths[page])
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)
        self.is_favorite()


# ============================================== Set a PDF or Job instruction as a default ===============================================================


    def set_default_instruction(self):
        """ Set a pdf as a defautl, save the selected pdf, convert it to png images and 
            save the path of the pdf in a file named 'default.txt',
            this way the application can read it in the future
        """

        file_options = QFileDialog.Options()
        file_options |= QFileDialog.DontUseNativeDialog
        path1, _ = QFileDialog.getOpenFileName(  self,
                                                'Select a PDF',   # Title of the window
                                                'assets/pdf/example.pdf', # Default filename to search
                                                'PDF Files (*.pdf)')    # Filter of file type
                                                # options=file_options)

        if path1:
            global favorites; favorites = (os.path.basename(path1)).split('.')[0]

            file_name = os.path.basename(path1)   # Get the filename
            file_name1 = file_name.split('.')[0] # File name without pdf extension 
            try:
                new_pdf_folder = os.path.join('assets/images', file_name1) # Create a folder with the file name
                os.makedirs(new_pdf_folder)
            except FileExistsError: pass

            try:
                pdf_dest_path = os.path.join('assets/pdf', file_name)   # Set the path to save the selected pdf
                shutil.copy(path1, pdf_dest_path)   # Copy the pdf from the FileDialog to the project path
            except shutil.SameFileError: pass   # If the file has already saved, skip

            self.save_pdf_image(path1, f'assets/images/{os.path.basename(favorites)}', f'{os.path.basename(favorites)}')

            list_ = sorted(f'assets/images/{os.path.basename(favorites)}/{text}' for text in os.listdir(f'assets/images/{os.path.basename(favorites)}/'))
            
            global image_paths; image_paths = sorted(list_, key=lambda x : int(x.split('_')[-1].split('.')[0]))
            
            with open('assets/default.txt', 'w') as default_file:
                default_file.write(pdf_dest_path)   # Write in a text file the path where is the new default pdf
            default_file.close()

            self.image_index = 0    # To show the pdf in the first page

            global images_copy; images_copy = image_paths
            global favorites_copy; favorites_copy = favorites

            global activate_favorites; activate_favorites = False
            
            b5.hide(); b4.show(); b3.show()
            
            self.show_image(self.image_index)   # Call the function to show the image

            self.setWindowTitle(f'{os.path.basename(favorites)}: {employee_number}')


# ====================================================== File Dialog to OPEN pdf files =======================================================================


    def ask_open_file(self):
        """ Save only the images of the selected pdf, if the pdf haven't been saved,
            the images will be saved in a folder named 'temporal_images', and
            every time that a new pdf is open the temporal images will be deleted,
            but if the open pdf is saved and located in the folder 'assets/pdf'
            the application will open that images and won't will create temporal images,
            maintaining the favorites and loading more faster the images
        """

        file_options = QFileDialog.Options()
        file_options |= QFileDialog.DontUseNativeDialog
        path1, _ = QFileDialog.getOpenFileName(  self,
                                                'Open a PDF',   # Title of the window
                                                'assets/pdf/example.pdf', # Default filename to search
                                                'PDF Files (*.pdf)')    # Filter of file type
                                                # options=file_options)

        if path1:
            file_name = os.path.basename(path1).split('.')[0]
            
            shutil.rmtree('assets/temporal_images/'); os.makedirs(os.path.join('assets', 'temporal_images'))

            if not os.path.exists(f'assets/images/{file_name}/'):
                self.save_pdf_image(path1, 'assets/temporal_images', 'image')
                list_ = sorted(f'assets/temporal_images/{text}' for text in os.listdir(f'assets/temporal_images/'))

            else:
                list_ = sorted(f'assets/images/{file_name}/{i}' for i in os.listdir(f'assets/images/{file_name}/'))
                global favorites; favorites = file_name
                b3.show()

            self.image_index = 0    # To show the pdf in the first page
            
            global image_paths; image_paths = sorted(list_, key=lambda x : int(x.split('_')[-1].split('.')[0]))

            global images_copy; images_copy = image_paths
            global favorites_copy; favorites_copy = favorites

            global activate_favorites; activate_favorites = False
            
            b5.hide(); b4.show()
            
            self.show_image(self.image_index)   # Call the function to show the image

            self.setWindowTitle(f'{os.path.basename(favorites)}: {employee_number}')


# ===================================================== File Dialog to SAVE pdf files ==================================================================


    def save_pdf(self):
        """ Open a file dialog and save the selected pdf in the folder 'assets/pdf'
            and convert if to images, then a question dialog will appear, and the user can
            deicide if open or no the pdf saved before.
        """

        file_options = QFileDialog.Options()
        file_options |= QFileDialog.DontUseNativeDialog
        path1, _ = QFileDialog.getOpenFileName(  self,
                                                'Save a PDF',   # Title of the window
                                                'example.pdf', # Default filename to search
                                                'PDF Files (*.pdf)')    # Filter of file type
                                                # options=file_options)

        if path1:
            global favorites; favorites = (os.path.basename(path1)).split('.')[0]

            file_name1 = os.path.basename(path1)    # Get the filename
            file_name = file_name1.split('.')[0] # File name without pdf extension
            try:
                new_pdf_folder = os.path.join('assets/images', file_name) # Create a folder with the file name
                os.makedirs(new_pdf_folder)
            except FileExistsError: pass

            try:
                pdf_dest_path = os.path.join('assets/pdf', file_name1)   # Set the path to save the selected pdf
                shutil.copy(path1, pdf_dest_path)   # Copy the pdf from the FileDialog to the project path
            except shutil.SameFileError: pass # If the file is already saved with that name, skip

            self.save_pdf_image(path1, f'assets/images/{os.path.basename(favorites)}', f'{os.path.basename(favorites)}')

            list_ = sorted(f'assets/images/{os.path.basename(favorites)}/{text}' for text in os.listdir(f'assets/images/{os.path.basename(favorites)}/'))
            
            global image_paths; image_paths = sorted(list_, key=lambda x : int(x.split('_')[-1].split('.')[0]))

            self.open_pdf_question()

            global activate_favorites; activate_favorites = False
            
            b5.hide(); b4.show(); b3.show()

            self.setWindowTitle(f'{os.path.basename(favorites)}: {employee_number}')


# ============================================== MessageBox to ask if open the pdf when it's saved =====================================================


    def open_pdf_question(self):
        """ Message box to ask the user if they want to open the saved pdf
        """

        msg_open = QMessageBox() # Declare as MessageBox
        response = msg_open.question(self, 'Open PDF?', # Window title
                                    'Do you want to open the saved PDF now?',   # Text inside the messagebox
                                    msg_open.Yes | msg_open.No) # Possible answer
        if response == msg_open.Yes: self.image_index = 0; self.show_image(self.image_index)  # Call the function if the answer was 'yes'
        else:
            global favorites, image_paths
            favorites = favorites_copy
            list_ = sorted(f'assets/images/{os.path.basename(favorites)}/{text}' for text in os.listdir(f'assets/images/{os.path.basename(favorites)}/'))
            image_paths = sorted(list_, key=lambda x : int(x.split('_')[-1].split('.')[0]))

            self.image_index = 0
            self.show_image(self.image_index)
                                                                         # This is for ensure that makes no possible no navigate whit the buttons
                                                                                         # or save in favorites the file hasn't been open
        msg_open.setStyleSheet(messageBox_style)


# =================================================== Function to add pages to favorites ================================================================


    def add_to_favorite(self):
        """ Create a folder with the current name of the pdf, where the favorites images
            will be saved, copy the current image to the favorite folder of the user
        """

        global employee_number_path

        favorite_name = os.path.basename(favorites) # Get the name of the file, without the extension
        
        try: os.makedirs(os.path.join(f'{employee_number_path}', favorite_name))    # Try to make a folder with the name of the file
        except FileExistsError: pass    # If the folder exist yet, skip the creation of the folder
        try: shutil.copy(f"assets/images/{favorite_name}/{favorite_name}_{self.image_index}.png",    # Copy the image path located in the poject folder
                        f"{employee_number_path}/{favorite_name}/{favorite_name}_{self.image_index}.png") # Paste the image in the favorites folder
        except: pass

        if not activate_favorites: global count_; count_ += 1
        # print(count_)
    
        self.is_favorite()


# =========================================== Function to check if the current image is saved in favorites ===============================================


    def is_favorite(self):
        """ Read the path of the current image, and if it is in the favorites folder
            change the icon of the 'add fovorite button' , the user can add or delete the favorites
        """

        global employee_number_path
        if not activate_favorites:  # Gloabl variable, to know if we want to show only the favorites saved
            favorite_name = os.path.basename(favorites) # Get the name of the file, without the extension
            global count_
            if count_ > 1:
                b3.setStyleSheet(favorite_off)
                try:
                    delete_favorite = any(file == (f'{favorite_name}_{self.image_index}.png') for file in os.listdir(f'{employee_number_path}/{favorite_name}'))
                    if delete_favorite: os.remove(f'{employee_number_path}/{favorite_name}/{favorite_name}_{self.image_index}.png')
                except: pass
                count_ = 0
                # print(count_)
            else:
                try:
                    favorite_image = any(file == (f'{favorite_name}_{self.image_index}.png') for file in os.listdir(f'{employee_number_path}/{favorite_name}'))
                    if favorite_image: b3.setStyleSheet(favorite_on)
                    else: b3.setStyleSheet(favorite_off)
                except: 
                    b3.setStyleSheet(favorite_off)
                    

# ============================================================ Show the favorites =======================================================================


    def show_favorites(self):
        """ Clear the current list where are saved the images path and 
            asign it the paths of the favorites images,
            if there is no favorite images saved, show a message box
        """

        global employee_number_path
        global image_paths  # Must especify the 'global' and the name of the variable, otherwise, a new variable will be created
        
        if not os.path.isdir(f'{employee_number_path}/{os.path.basename(favorites)}/'): self.show_alert()  # Show the messagebox if there is no favorites saved yet
        elif not os.path.isdir(f'{employee_number_path}/'): self.show_alert()
        elif not os.listdir(f'{employee_number_path}/{os.path.basename(favorites)}/'): self.show_alert()
        elif len(image_paths) < 1: self.show_alert()
        else:
            global activate_favorites; activate_favorites = True
        
            favorites_list = sorted(f'{employee_number_path}/{os.path.basename(favorites)}/{image}' for image in os.listdir(f'{employee_number_path}/{os.path.basename(favorites)}/'))
            b3.setStyleSheet(favorite_on)
            self.image_index = 0

            image_paths = sorted(favorites_list, key=lambda x: int(x.split('_')[-1].split('.')[0]))
        
            # print(image_paths,'\n')
            
            self.show_image(self.image_index)
            b4.hide()   # Hide the button
            b5.show()   # Show the button


# ============================================================ Return and show all images instead of favorites ===========================================


    def show_all(self):
        """ Clear the list and asign it the path of all the images
        """

        global activate_favorites
        if activate_favorites:
            activate_favorites = False
            l = sorted(f'assets/images/{os.path.basename(favorites)}/{image}' for image in os.listdir(f'assets/images/{os.path.basename(favorites)}'))
            self.image_index = 0

            global image_paths
            image_paths = sorted(l, key=lambda x: int(x.split('_')[-1].split('.')[0]))

            # print(image_paths)
            self.show_image(self.image_index)
            self.is_favorite()
            b5.hide(); b4.show()


# =============================================== Message box if there is no favorites saved yet =======================================================


    def show_alert(self):
        """ Message box if the user haven't save a pdf and try to add favorites
        """

        msg_ = QMessageBox() # Declare as MessageBox
        msg_.setIcon(QMessageBox.Warning)    # Set the type of MessageBox
        msg_.setText('No favorites saved yet!!!') # Text inside the MessageBox
        msg_.setWindowTitle('No Favorites')   # Set the title of the window
        msg_.setFont(QFont(f'{font_}', 11))
        msg_.setStyleSheet(messageBox_style)
        retval = msg_.exec_()    # Execute the MessageBox window

    
    def show_alert2(self):
        """ Message box if the user haven't save a pdf and try to add favorites
        """

        msg_ = QMessageBox() # Declare as MessageBox
        msg_.setIcon(QMessageBox.Warning)    # Set the type of MessageBox
        msg_.setText('No PDF saved yet!!!') # Text inside the MessageBox
        msg_.setWindowTitle('No PDF')   # Set the title of the window
        msg_.setFont(QFont(f'{font_}', 11))
        msg_.setStyleSheet(messageBox_style)
        retval = msg_.exec_()    # Execute the MessageBox window


# ======================================================== Input dialog to ask employee number ===========================================================


    def employee_number(self):
        """ When start the program, ask the user for their employee number,
            this is just for make a custom folder where their favorites images will be saved,
            if the input wasn't a number, automatically change it to default user
        """

        global default_number
        global employee_number
        global employee_number_path

        try:
            employee_number, done = QInputDialog.getText(self, 'Employee Number', 'Enter your employee number:')
            if done:
                if employee_number:
                    try:
                        employee_number = int(employee_number)
                        if type(employee_number) == int:
                            try: os.makedirs(os.path.join('assets/users', f'{employee_number}'))
                            except FileExistsError: pass
                        default_number = False
                    except: employee_number = 'default user'
                else: employee_number = 'default user'
            else: employee_number = 'default user'

            if default_number: employee_number_path = f'assets/favorites'
            else: employee_number_path = f'assets/users/{employee_number}/favorites'
        except: pass


# ================================================================= GUI Interface =========================================================================


    def initGUI(self):
        """ Start the application and try to read the 'default.txt' file,
            if there is no default pdf, show a text label, change the title
            of the window depending of the name of the pdf and employee number
        """

        global employee_number

        self.setStyleSheet(messageBox_style)
        self.setFont(QFont(font_))
        
        self.setGeometry(450, 100, 1000, 900)    # X position, Y position, Width, Height
        
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(25, 35, 950, 720)    # X position, Y position, width, height
        self.label.setText('Please select or save a PDF')   # Defautl text in the window
        self.label.setFont(QFont(font_))
        self.label.setStyleSheet(f'border-radius: {border}; border: 1px solid {color_}; background-color: {bg_color}; color: {color_};')

        self.line = QLineEdit(self)
        self.line.move(480, 770)
        self.line.resize(100, 40)
        self.line.setStyleSheet(f'border-radius: {border}; border: 1px solid {color_}; background-color: {bg_color}; color: {color_};')

        self.menu_config()  # Call the function
        self.buttons()  # Call the function

        self.image_index = 0    # The initial page of the pdf
        self.employee_number()
        
        try: self.show_image(self.image_index)   # If default.txt was not created yet, skip
        except: pass

        self.is_favorite()

        if os.path.isfile('assets/default.txt'): self.setWindowTitle(f'{os.path.basename(favorites)}: {employee_number}'); b3.show()
        else: self.setWindowTitle(f'Job Instruction: {employee_number}'); self.suggest_message()

        self.show()


# ============================================================= Menu for the GUI ===========================================================================


    def menu_config(self):
        """ Style and configuration for the menu of the application
        """

        menuBar_style = f"""
        QMenuBar
        {{
            background-color: {bg_color};
            color: {color_};
        }}
        QMenuBar::item
        {{
            spacing: 3px;
            padding: 2px 10px;
            background-color: {bg_color};
            color: {color_};
            border-radius: 5px;
        }}
        QMenuBar::item:selected
        {{
            background-color: {color_};
            color: {bg_color};
        }}
        QMenuBar::item:pressed
        {{
            background-color: white;
        }}
        
        
        QMenu
        {{
            background-color: {bg_color};
            border: 1px solid black;
            margin: 2px;
        }}
        QMenu::item
        {{
            background-color: {bg_color};
            color: {color_};
        }}
        QMenu::item:selected
        {{
            background-color: {color_};
            color: {bg_color}
        }}
        """

        menu = self.menuBar()
        options_menu = menu.addMenu('Options')
        help_menu = menu.addMenu('Help')       
        menu.setFont(QFont(f'{font_}', 11))
        menu.setCursor(Qt.PointingHandCursor)    # Change the type of the cursor
        menu.setStyleSheet(menuBar_style)

        options_actions = {  # Option fot the menu and action to execute
            'Open': self.ask_open_file,
            'Add Instruction': self.save_pdf,
            'Set default Instruction': self.set_default_instruction,
            'Exit': self.close
        }
        
        help_actions = {    # Option fot the menu and action to execute
            'About': self.show_info,
            'Welcome': self.suggest_message,
            'License': self.show_license
        }

        for option, action in options_actions.items():
            op = QAction(option, self)
            op.triggered.connect(action)
            options_menu.addAction(op)
        
        for option, action in help_actions.items():
            op = QAction(option, self)
            op.triggered.connect(action)
            help_menu.addAction(op)


# ============================================================== Buttons Functions ====================================================================


    def buttons(self):
        """ Buttons, their style and function cunfiguration
        """

        global button_style, favorite_on, favorite_off, menuBar_style

        button_style = f"""
        QPushButton
        {{
            border-radius: {border};
            border: 1px solid {color_};
            background-color: {bg_color};
            color: {color_};
        }}
        QPushButton::hover
        {{
            border-radius: {border};
            border: 1px solid {color_};
            background-color: {color_};
            color: {bg_color};
        }}
        """
        search_b_style = f"""
        QPushButton
        {{
            background-image: url(buttons-images/search.png);
            border-radius: {border};
            border: 1px solid {color_};
            background-color: {bg_color};
            color: {color_};
        }}
        QPushButton::hover
        {{
            background-image: url(buttons-images/search.png);
            border-radius: {border};
            border: 1px solid {color_};
            background-color: {color_};
            color: {bg_color};
        }}
        """
        favorite_on = f"""
        QPushButton
        {{
            background-image: url(buttons-images/favorite-true.png);
            border-radius: {border};
            border: 2px solid {color_};
            background-color: {bg_color};
            color: {color_};
        }}
        QPushButton::hover
        {{
            background-image: url(buttons-images/favorite-true.png);
            border-radius: {border};
            border: 2px solid {color_};
            background-color: {color_};
            color: {bg_color};
        }}
        """

        favorite_off = f"""
        QPushButton
        {{
            background-image: url(buttons-images/favorite-false.png);
            border-radius: {border};
            border: 2px solid {color_};
            background-color: {bg_color};
            color: {color_};
        }}
        QPushButton::hover
        {{
            background-image: url(buttons-images/favorite-false.png);
            border-radius: {border};
            border: 2px solid {color_};
            background-color: {color_};
            color: {bg_color};
        }}
        """

        b1 = QPushButton('<', self) # Text in the button
        b1.setGeometry(50, 830, 80, 40)    # X position, Y position, width, height
        b1.clicked.connect(self.show_previous_page) # Funtion to execute when clicked
        b1.setStyleSheet(button_style)
        b1.setFont(QFont(f'{font_}', 25))
        b1.setCursor(Qt.PointingHandCursor)    # Change the type of the cursor
    

        b2 = QPushButton('>', self) # Text in the button
        b2.setGeometry(850, 830, 80, 40)   # X position, Y position, width, height
        b2.clicked.connect(self.show_nex_page)  # Funtion to execute when clicked
        b2.setFont(QFont(f'{font_}', 20))
        b2.setCursor(Qt.PointingHandCursor)    # Change the type of the cursor
        b2.setStyleSheet(button_style)


        global b3
        b3 = QPushButton('', self) # Text in the button
        b3.setGeometry(920, 40, 42, 40)     # X position, Y position, width, height
        b3.clicked.connect(self.add_to_favorite)    # Funtion to execute when clicked
        b3.setCursor(Qt.PointingHandCursor)    # Change the type of the cursor
        b3.hide()


        global b4
        b4 = QPushButton('Show Favorites', self)    # Text in the button
        b4.setGeometry(420, 830, 160, 40)   # X position, Y position, width, height
        b4.clicked.connect(self.show_favorites) # Funtion to execute when clicked
        b4.setFont(QFont(f'{font_}', 12))
        b4.setCursor(Qt.PointingHandCursor)    # Change the type of the cursor
        b4.setStyleSheet(button_style)


        global b5
        b5 = QPushButton('Show All', self)    # Text in the button
        b5.setGeometry(420, 830, 160, 40)   # X position, Y position, width, height
        b5.clicked.connect(self.show_all) # Funtion to execute when clicked
        b5.setFont(QFont(f'{font_}', 12))
        b5.setCursor(Qt.PointingHandCursor)    # Change the type of the cursor
        b5.setStyleSheet(button_style)
        b5.hide()   # Hide the button
    

        b6 = QPushButton('', self) # Text in the button
        b6.setGeometry(420, 770, 42, 40)     # X position, Y position, width, height
        b6.clicked.connect(self.goto_page)    # Funtion to execute when clicked
        b6.setCursor(Qt.PointingHandCursor)    # Change the type of the cursor
        b6.setStyleSheet(search_b_style)
        

    def show_previous_page(self):
        """ Move the page, show the previous and execute the function to
            determine if it is a favorite
        """

        if self.image_index > 0:
            self.image_index -= 1
            self.show_image(self.image_index)
            self.is_favorite()  # Check if the current image is saved in favorites


    def show_nex_page(self):
        """ Move the page, show the next and execute the function to
            determine if it is a favorite
        """

        if self.image_index < len(image_paths) - 1:
            self.image_index += 1
            self.show_image(self.image_index)
            self.is_favorite()  # Check if the current image is saved in favorites
    

    def goto_page(self):
        """ Go to the especific page, and not allow to navigate with nagative number
        """

        try:
            page_number = int(self.line.text())
            self.image_index = page_number - 1
            if not self.image_index < 0:
                self.show_image(self.image_index)
        except: pass


# ============================================================= Secondary Window to show favorites ======================================================


if __name__ == '__main__':   
    app = QApplication(sys.argv)
    window = JobInstructionPDF()
    # window.show()
    sys.exit(app.exec())
