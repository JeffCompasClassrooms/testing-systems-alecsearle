import os
import pytest
from mydb import MyDB

def describe_MyDB():

    def describe_init():
        
        def it_creates_new_database_file_when_file_does_not_exist():
            # setup
            test_file = "test_init_new.db"
            if os.path.isfile(test_file):
                os.remove(test_file)
            
            # exercise
            db = MyDB(test_file)
            
            # verify
            assert os.path.isfile(test_file)
            
            # teardown
            os.remove(test_file)

        def it_does_not_overwrite_existing_database_file():
            # setup
            test_file = "test_init_existing.db"
            db1 = MyDB(test_file)
            db1.saveStrings(["original", "data"])
            
            # exercise
            db2 = MyDB(test_file)
            
            # verify
            loaded_data = db2.loadStrings()
            assert loaded_data == ["original", "data"]
            
            # teardown
            os.remove(test_file)

        def it_initializes_empty_database_for_new_file():
            # setup
            test_file = "test_init_empty.db"
            if os.path.isfile(test_file):
                os.remove(test_file)
            
            # exercise
            db = MyDB(test_file)
            
            # verify
            data = db.loadStrings()
            assert data == []
            
            # teardown
            os.remove(test_file)

    def describe_loadStrings():
        
        def it_loads_empty_array_from_new_database():
            # setup
            test_file = "test_load_empty.db"
            if os.path.isfile(test_file):
                os.remove(test_file)
            db = MyDB(test_file)
            
            # exercise
            result = db.loadStrings()
            
            # verify
            assert result == []
            assert isinstance(result, list)
            
            # teardown
            os.remove(test_file)

        def it_loads_strings_that_were_previously_saved():
            # setup
            test_file = "test_load_saved.db"
            if os.path.isfile(test_file):
                os.remove(test_file)
            db = MyDB(test_file)
            test_data = ["hello", "world", "testing"]
            db.saveStrings(test_data)
            
            # exercise
            result = db.loadStrings()
            
            # verify
            assert result == test_data
            assert len(result) == 3
            
            # teardown
            os.remove(test_file)

        def it_loads_strings_with_special_characters():
            # setup
            test_file = "test_load_special.db"
            if os.path.isfile(test_file):
                os.remove(test_file)
            db = MyDB(test_file)
            special_data = ["hello@world", "test#123", "data$%^"]
            db.saveStrings(special_data)
            
            # exercise
            result = db.loadStrings()
            
            # verify
            assert result == special_data
            
            # teardown
            os.remove(test_file)

    def describe_saveStrings():
        
        def it_saves_array_of_strings_to_database():
            # setup
            test_file = "test_save_array.db"
            if os.path.isfile(test_file):
                os.remove(test_file)
            db = MyDB(test_file)
            test_data = ["item1", "item2", "item3"]
            
            # exercise
            db.saveStrings(test_data)
            
            # verify
            loaded = db.loadStrings()
            assert loaded == test_data
            
            # teardown
            os.remove(test_file)

        def it_overwrites_existing_data_in_database():
            # setup
            test_file = "test_save_overwrite.db"
            if os.path.isfile(test_file):
                os.remove(test_file)
            db = MyDB(test_file)
            db.saveStrings(["old1", "old2"])
            
            # exercise
            new_data = ["new1", "new2", "new3"]
            db.saveStrings(new_data)
            
            # verify
            loaded = db.loadStrings()
            assert loaded == new_data
            assert "old1" not in loaded
            
            # teardown
            os.remove(test_file)

        def it_saves_empty_array_to_database():
            # setup
            test_file = "test_save_empty.db"
            if os.path.isfile(test_file):
                os.remove(test_file)
            db = MyDB(test_file)
            db.saveStrings(["data"])
            
            # exercise
            db.saveStrings([])
            
            # verify
            loaded = db.loadStrings()
            assert loaded == []
            
            # teardown
            os.remove(test_file)

        def it_persists_data_across_multiple_instances():
            # setup
            test_file = "test_save_persist.db"
            if os.path.isfile(test_file):
                os.remove(test_file)
            db1 = MyDB(test_file)
            test_data = ["persistent", "data"]
            
            # exercise
            db1.saveStrings(test_data)
            db2 = MyDB(test_file)
            
            # verify
            loaded = db2.loadStrings()
            assert loaded == test_data
            
            # teardown
            os.remove(test_file)

    def describe_saveString():
        
        def it_appends_string_to_empty_database():
            # setup
            test_file = "test_append_empty.db"
            if os.path.isfile(test_file):
                os.remove(test_file)
            db = MyDB(test_file)
            
            # exercise
            db.saveString("first")
            
            # verify
            loaded = db.loadStrings()
            assert loaded == ["first"]
            
            # teardown
            os.remove(test_file)

        def it_appends_string_to_existing_data():
            # setup
            test_file = "test_append_existing.db"
            if os.path.isfile(test_file):
                os.remove(test_file)
            db = MyDB(test_file)
            db.saveStrings(["existing1", "existing2"])
            
            # exercise
            db.saveString("new_item")
            
            # verify
            loaded = db.loadStrings()
            assert loaded == ["existing1", "existing2", "new_item"]
            assert len(loaded) == 3
            
            # teardown
            os.remove(test_file)

        def it_appends_multiple_strings_sequentially():
            # setup
            test_file = "test_append_multiple.db"
            if os.path.isfile(test_file):
                os.remove(test_file)
            db = MyDB(test_file)
            
            # exercise
            db.saveString("first")
            db.saveString("second")
            db.saveString("third")
            
            # verify
            loaded = db.loadStrings()
            assert loaded == ["first", "second", "third"]
            assert loaded[0] == "first"
            assert loaded[2] == "third"
            
            # teardown
            os.remove(test_file)

        def it_preserves_order_of_appended_strings():
            # setup
            test_file = "test_append_order.db"
            if os.path.isfile(test_file):
                os.remove(test_file)
            db = MyDB(test_file)
            db.saveStrings(["a", "b"])
            
            # exercise
            db.saveString("c")
            db.saveString("d")
            
            # verify
            loaded = db.loadStrings()
            assert loaded == ["a", "b", "c", "d"]
            
            # teardown
            os.remove(test_file)