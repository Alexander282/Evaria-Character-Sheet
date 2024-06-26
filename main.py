import dearpygui.dearpygui as dpg
import json


# Activation - Only runs once when started (hopefully)
class ActiveCharFile:  # Class we use for an Active file, we should only have one of these.
    def __init__(self, name, file_path, data=None):  # format in comments for next 2 lines
        if data is None:
            data = {}
        self.name = name  # 'name.json'
        self.file_path = file_path
        self.data = data  # {Stats: {Strength: 10}}

    def get_all(self, request):  # return the info in a dictionary
        info = {'name': self.name, 'data': self.data, 'file_path': self.file_path}
        return info[request]

    def get_value_by_path(self, path):
        value = self.get_all('data')
        for i in range(len(path)):
            value = value[path[i]]
        return value

    def set_value_in_location(self, path, value):
        dic = self.get_all('data')
        for key in path[:-1]:
            dic = dic.setdefault(key, {})
        dic[path[-1]] = value

    def del_value_in_location(self, path):
        dic = self.get_all('data')
        for key in path[:-1]:
            dic = dic.setdefault(key, {})
        del dic[path[-1]]


active_data = ActiveCharFile('', {})  # Assign the class to active_data

dpg.create_context()  # Creates context, necessary for DPG


# Usage - Ran throughout the program's work.
# Functions - define functions to be used later here.
def save_file(sender, app_data):  # Overwrites the file
    active_data.name = app_data['file_name']
    active_data.file_path = app_data['file_path_name']
    file = open(active_data.get_all('file_path'), mode='w')
    json.dump(active_data.get_all('data'), file, ensure_ascii=False, indent=4)
    file.close()


def load_file(sender, app_data):
    # print(app_data)
    if active_data.name != '':
        info = {'file_path_name': active_data.get_all("file_path"), 'file_name': active_data.get_all('name')}
        save_file(sender, info)

    dpg.delete_item("Primary_Tab_Bar", children_only=True)
    dpg.add_tab_button(label="+", tag="Add_Tab_Button", parent="Primary_Tab_Bar", callback=new_tab, trailing=True)
    file = open(app_data['file_path_name'], mode='r')  # Open the file, specified by name
    active_data.name = app_data['file_name']
    active_data.file_path = app_data['file_path_name']
    active_data.data = json.load(file)
    file.close()
    open_file(active_data.get_all("data"))


def open_file(file_data):  # Reads the current active file and creates tabs because of it. file_data is that info
    for tab_key in file_data.keys():
        load_tab(file_data, tab_key)


def load_tab(file_data, tab_key):
    tab_type = file_data[tab_key]['Type']
    tab_label = file_data[tab_key]['Label']
    tab_content = file_data[tab_key]['Content']
    path_tag = tab_key + '-' + tab_type
    dpg.add_tab(label=tab_label, parent="Primary_Tab_Bar", tag=path_tag)
    # print(tab_content)
    generate_tab_content(path_tag, tab_content)


def create_new_tab():  # Creates a tab, assigning a value to it
    tab_type, tab_name = [dpg.get_value("New_Tab_Combo"), dpg.get_value("New_Tab_Input")]  # tab_type
    file_tab_key = 1
    if len(active_data.get_all("data")) > 0:
        key_values = [int(i) for i in active_data.get_all("data").keys()]
        file_tab_key = max(key_values) + 1
    # dpg.add_string_value()
    if tab_type != "Custom":
        path_tag = str(file_tab_key) + "-" + tab_type
        dpg.add_tab(label=tab_name, parent="Primary_Tab_Bar", tag=path_tag)
        active_data.data[str(file_tab_key)] = {"Label": tab_name, "Type": tab_type, "Content": {}}
    else:
        path_tag = str(file_tab_key) + "-" + tab_type
        dpg.add_tab(label=tab_name, parent="Primary_Tab_Bar", tag=path_tag)
        active_data.data[str(file_tab_key)] = {"Label": tab_name, "Type": tab_type, "Content": {}}
    generate_tab_content(path_tag, {})
    dpg.configure_item("New_Tab_Creator", show=False)


# def create_secondary_stats_table(current_tab_data, root_tag, table_path_tag):
#     # print(current_tab_data)
#     unique_cases = ["Name", "Base", "Secondary", "Total", "Modifier"]
#     for main_stat_key in current_tab_data:  # go through each stat key (stored as numbers)
#         with dpg.table_row(parent=table_path_tag):
#             for attribute in current_tab_data[main_stat_key]:  # go through each attribute (name, Base value, Secondary stats, etc.)
#                 item_tag = (root_tag + main_stat_key + "-" + attribute)
#                 if attribute not in unique_cases:  # most unique cases aren't actively editable
#                     # print(attribute)
#                     current_cell_data = current_tab_data[main_stat_key][attribute]
#                     dpg.add_input_int(default_value=current_cell_data, callback=calculate_total, tag=item_tag, width=-1)
#                 elif attribute == "Name":  # secondary stats need to be done on their own because they're a different case
#                     current_cell_data = current_tab_data[main_stat_key][attribute]
#                     dpg.add_input_text(default_value=current_cell_data, callback=edit_name, tag=item_tag, width=-1)
#                 elif attribute == "Base":
#                     target_source = item_tag.rsplit('-', 3)[0] + '-Total'
#                     dpg.add_text(source=target_source, tag=item_tag)
#                 elif attribute == "Secondary":
#                     create_secondary_stats_table(current_tab_data[main_stat_key]["Secondary"], item_tag + "-", table_path_tag)
#                 else:  # secondary stats need to be done on their own because they're a different case
#                     current_cell_data = current_tab_data[main_stat_key][attribute]
#                     dpg.add_text(default_value=current_cell_data, tag=item_tag)
#             with dpg.table_row(parent=table_path_tag):
#                 dpg.add_button(label='+', width=-1, callback=create_new_stat)


def generate_tab_content(path_tag, current_tab_data):
    # print(current_tab_data)
    root = path_tag.split('-')[0]  # lowest point where we are right now, used for naming the data input tags
    tab_type = path_tag.split('-')[-1]
    if tab_type == "Stats":
        allowed_attributes = ["Base", "Racial", "Other", "Total", "Modifier"]  # ensures that no other things appear or are used
        # TO-DO: change from table to groups and windows, since tables would make this harder than it should be.
        with dpg.child_window(border=True, tag=(path_tag + "-Window"), parent=path_tag, height=100):
            with dpg.group(horizontal=True, horizontal_spacing=100):
                dpg.add_text(default_value="Stat")  # creates the Header row
                for attribute in allowed_attributes:
                    dpg.add_text(default_value=attribute)
            dpg.add_button(label='+', width=-1, callback=create_new_stat, user_data=root + "-Content")
            create_stat_window(current_tab_data, root + "-Content", (path_tag + "-Window"))



def create_new_stat(sender, app_data, item_tag):
    # remove create new button
    current_tab_data = active_data.get_value_by_path(item_tag.split("-"))
    new_key_index = "1"
    if len(current_tab_data.keys()) > 0:
        key_values = [int(i) for i in current_tab_data.keys()]
        new_key_index = str(max(key_values) + 1)
    # create a stat row
    window_tag = dpg.get_item_alias(dpg.get_item_parent(sender))
    dpg.set_item_height(window_tag, dpg.get_item_height(window_tag) + 130)
    new_stat_data = {'Name': "New" + new_key_index, 'Base': 10, 'Racial': 0, 'Other': 0, 'Total': 10, 'Modifier': '+0', 'Secondary': {}}
    new_location = (item_tag + "-" + new_key_index).split("-")
    active_data.set_value_in_location(new_location, new_stat_data)
    create_stat_window({new_key_index: new_stat_data}, item_tag, window_tag)
    # recreate button


def delete_stat(sender):
    parent_group = dpg.get_item_parent(sender)
    parent_window = dpg.get_item_parent(parent_group)
    previous_stat_window = dpg.get_item_parent(parent_window)
    # reduces the height of the previous item by the height of what just got removed
    dpg.set_item_height(previous_stat_window, dpg.get_item_height(previous_stat_window) - dpg.get_item_height(parent_window))
    item_location = dpg.get_item_alias(parent_group).split("-")[:-1]
    active_data.del_value_in_location(item_location)
    dpg.delete_item(parent_window)


def create_stat_window(current_tab_data, item_tag, parent_tag):
    # create a child window in the set location
    for main_stat_key in current_tab_data:  # go through each stat key (stored as numbers)
        amount_of_secondaries = len(current_tab_data[main_stat_key]["Secondary"])
        child_window_parent_tag = parent_tag + "-" + main_stat_key + '-Window'
        with dpg.child_window(border=True, parent=parent_tag, height=130*(amount_of_secondaries+1), tag=child_window_parent_tag):
            dpg.add_button(label='+', width=-1, callback=create_new_stat, user_data=item_tag)
            print(item_tag)
            group_tag = (item_tag + '-' + str(main_stat_key) + "-group")
            dpg.add_group(horizontal=True, tag=group_tag)
            for attribute in current_tab_data[main_stat_key]:  # go through each attribute (name, Base value, Secondary stats, etc.)
                new_item_tag = (item_tag + "-" + main_stat_key + "-" + attribute)
                current_cell_data = current_tab_data[main_stat_key][attribute]
                if attribute == "Name":  # secondary stats need to be done on their own because they're a different case
                    dpg.add_input_text(default_value=current_cell_data, callback=edit_name, tag=new_item_tag, width=100, parent=group_tag)
                elif attribute == "Secondary":
                    create_stat_window(current_tab_data[main_stat_key]["Secondary"], new_item_tag, child_window_parent_tag)
                elif attribute in ["Total", "Modifier"]:
                    # dpg.add_int_value(parent="Value_Storage", tag=item_tag + "Value", default_value=current_cell_data)
                    dpg.add_text(tag=new_item_tag, default_value=current_cell_data, parent=group_tag)  # source=item_tag + "Value")
                else:
                    dpg.add_input_int(default_value=current_cell_data, callback=calculate_total, tag=new_item_tag, width=100, parent=group_tag)
            dpg.add_button(label='X', width=-1, callback=delete_stat, parent=group_tag)
            dpg.set_item_height(parent_tag, dpg.get_item_height(parent_tag) + dpg.get_item_height(child_window_parent_tag))


def edit_name(sender, app_data):
    path = dpg.get_item_alias(sender).split("-")
    active_data.set_value_in_location(path, app_data)


def calculate_total(sender):
    tag_template = dpg.get_item_alias(sender).rsplit("-", 1)[0]
    path = dpg.get_item_alias(sender).split("-")[:-1]
    row_attributes = active_data.get_value_by_path(path)  # there's got to be a better way, but I don't know it yet...
    sum_value = 0
    unique_cases = ["Name", "Secondary", "Total", "Modifier"]
    # print(active_data.get_all("data"))
    for attribute in row_attributes:
        location = path + [attribute]
        if attribute not in unique_cases:
            attribute_value = int(dpg.get_value(tag_template + "-" + attribute))
            sum_value += attribute_value
            active_data.set_value_in_location(location, attribute_value)
        elif attribute == "Total":
            dpg.set_value(tag_template + "-" + attribute, sum_value)
            active_data.set_value_in_location(location, sum_value)
        elif attribute == "Modifier":
            modifier_value = int(sum_value / 2 - 5)
            if modifier_value < 0:
                modifier_text = str(modifier_value)
            else:
                modifier_text = "+" + str(modifier_value)
            dpg.set_value((tag_template + "-" + attribute), modifier_text)
            active_data.set_value_in_location(location, modifier_text)


def cancel_load(sender, app_data):
    print('Cancel was clicked.')
    print("Sender: ", sender)
    print("App Data: ", app_data)
    print(active_data.get_all("data"))


def new_tab():  # Opens the new tab creator window
    dpg.configure_item("New_Tab_Creator", show=True)


dpg.add_value_registry(tag="Value_Storage")

# with dpg.window(tag="Rename_Window"):
#    dpg.add_input_text(tag='New_Name')
#    dpg.add_button(tag='Close_Rename', label='Cancel', callback=hide_rename_view)
#    dpg.add_button(tag='Submit_Rename', label='Cancel')

with dpg.file_dialog(directory_selector=False, show=False, callback=save_file, cancel_callback=cancel_load, tag="save_file_explorer", width=700, height=400,
                     default_filename=active_data.get_all("name")):
    dpg.add_file_extension(".json", color=(128, 255, 128, 255), custom_text="[JSON]")

with dpg.file_dialog(directory_selector=False, show=False, callback=load_file, cancel_callback=cancel_load, tag="load_file_explorer", width=700, height=400,
                     default_filename=active_data.get_all("name")):
    dpg.add_file_extension(".json", color=(128, 255, 128, 255), custom_text="[JSON]")

with dpg.window(tag="Primary_Window", no_close=False):  # main window
    with dpg.menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="New")
            dpg.add_menu_item(label="Open", callback=lambda: dpg.show_item("load_file_explorer"))
            dpg.add_menu_item(label="Save", callback=lambda: dpg.show_item("save_file_explorer"))
    with dpg.tab_bar(tag="Primary_Tab_Bar"):
        dpg.add_tab_button(label="+", tag="Add_Tab_Button", callback=new_tab, trailing=True)

with dpg.window(label="New Tab Creator", show=False, tag="New_Tab_Creator", modal=True, no_collapse=True, width=200, height=300, pos=[100, 100]):  # Tab creation window
    dpg.add_combo(items=["Stats", "Custom"], tag="New_Tab_Combo", default_value="Custom")
    dpg.add_input_text(default_value="Enter custom tab here", tag="New_Tab_Input", parent="New_Tab_Creator")
    dpg.add_button(label="Enter", callback=create_new_tab)
    # read_file(active_data.getInfo("data"))
    # dpg.add_button(label="File", callback=lambda: dpg.show_item("load_file_explorer"))
# dpg.show_item("load_file_explorer")
dpg.create_viewport(title="Crow's Character Creator", width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary_Window", True)
dpg.start_dearpygui()
dpg.destroy_context()
