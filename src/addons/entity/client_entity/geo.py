from addons.helpers.errors import *

class Geometry:

    """ Geometry class which encapsulates client entity data related to the geometry of an entity

    """
    format_version = '1.12.0'

    def __init__(self, geo_data: dict, dummy: bool = False):
        """
        :param geo_data: The json data loaded from the geometry file
        """
        self.__geo_data: dict = geo_data
        self.__num_geos: int = len(self.__geo_data['minecraft:geometry']) if not dummy else 0
        self.__is_dummy: bool = dummy

    def get_geos(self) -> dict:
        """ Returns the geometry map of short_name: geometry_identifer for each geometry in the geometry file, then this map should be used in the client entity function to set the geometries

        :returns: A dictionary mapping the geometry name to its identifier for the client entity file
        """
        geo_names: dict = {}

        if self.__geo_data is None:
            geo_names['default'] = 'geometry.dummy'
            return geo_names

        try:
            for geo in self.__geo_data['minecraft:geometry']:
                # minecraft:geometry key is a list of dictionaries
                geo_name = geo['description']['identifier'].replace('geometry.cc_', '')
                # set the key value pair correctly in the textures property of the client entity json object
                if self.__num_geos == 1:
                    geo_names['default'] = geo['description']['identifier']

                else:
                    if not self.__is_dummy:
                        geo_names[geo_name] = geo['description']['identifier']
                    
        except KeyError:
            raise BadDataInputExcep('There is a problem with the entity\'s geometry file!')

        return geo_names

    def get_names(self) -> list[str]:
        """ Returns the list of geometry names for use in geometry arrays in the entity's render controller

        :return: list of geometry short-names defined in the client entity        
        """
        return [ f'Geometry.{x}' for x in list(self.get_geos()) ]

    def get_locators(self) -> dict:
        """ Returns the locator map for each locator in the geometry bones, then this map should be used in the client entity function to set the locators

        :param geo_data: The geometry dictionary loaded from the json file
        :return: dictionary of values
        """
        if not self.__geo_data:
            return None

        try:
            ce_locators = {}

            for geo in self.__geo_data['minecraft:geometry']:
                # minecraft:geometry key is a list of dictionaries
                bones = geo['bones']
                # loop through all the bones in each geometry object
                for bone in bones:
                    bone_name = bone['name']
                    # if the bone has a locator
                    if 'locators' in bone:
                        geo_locators = bone['locators']
                        # get the name and location of the locators
                        for name, location in geo_locators.items():
                            locator = {}
                            # location is a list of three values like [0,1,2]
                            locator[bone_name] = location
                            assert (len(location) == 3)
                            ce_locators[name] = locator
                    
                    else:
                        continue

        except AssertionError:
            raise BadDataInputExcep('There is a problem processing the locators of the geometry file!')

        except BadDataInputExcep as err:
            print(err)

        return ce_locators if len(ce_locators) >= 1 else None

    def get_bones(self) -> list[str]:

        bones = []
        if not self.__geo_data:
            return None
            
        try:
            for geo in self.__geo_data['minecraft:geometry']:
                geo_bones = geo['bones']

                for bone in geo_bones:
                    bones.append(bone['name'])
            
            assert (len(bones) >= 1)
            return bones

        except AssertionError:
            raise BadDataInputExcep('The entity does not have any bones!')

        except KeyError:
            raise BadDataInputExcep('There was an issue collecting the bones from the geometry file!')

        except BadDataInputExcep as err:
            print(err)