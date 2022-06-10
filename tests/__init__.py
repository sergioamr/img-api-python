from imgapi.imgapi import ImgAPI

############## Login with an user first ####################

testing_user = {
    'username': "python_unittest",
    'password': "123password!",
    'email': "unittest@img-api.com",
}

api = ImgAPI()
api.setup("http://localhost:5112/api", {})

user = api.create_user(testing_user)

############# Run tests ####################################
