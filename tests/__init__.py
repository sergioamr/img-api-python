from imgapi.imgapi import ImgAPI

############## Login with an user first ####################

testing_user = {
    'username': "python_unittest_1",
    'password': "123password!",
    'email': "unittest_1@img-api.com",
    'is_media_public': False,
    'is_public': False
}

api = ImgAPI()
api.setup("http://localhost:5112/api", {})

user = api.create_user(testing_user)

############# Run tests ####################################
