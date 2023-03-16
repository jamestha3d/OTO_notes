from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from .views import *
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from base.models import Tag

User = get_user_model()

class IndexTestCase(APITestCase):
    def test_index(self):
        response=self.client.get(reverse('publicNotes'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class NoteCreationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="tester1@tests.com", password="Testsubject@1#", username="testsubject1")
        self.public_notes = [
            Note.objects.create(title = "test note1", body = "this is public test note1 body", public = True, user = self.user),
            Note.objects.create(title = "test note2", body = "this is public test note2 body", public = True, user = self.user), 
            Note.objects.create(title = "test note3", body = "this is public test note3 body", public = True, user = self.user) 
        ] 
        self.sample_note = {
            "title": "note 1",
            "body": "sample note 1 black",
            "tag": "black"
            }
        self.sample_note2 = {
            "title": "note 2",
            "body": "sample note 2 blue",
            "tag": "blue"
            }
        self.sample_note3 = {
            "title": "note 3",
            "body": "sample note 3 blue",
            "tag": "blue"
            }
        self.sample_note4 = {
            "title": "note 4",
            "body": "sample note 4 black",
            "tag": "black"
            }
     
    #custom method to authenticate user for tests
    def authenticate(self):
        self.client.post(reverse('signUp'), {
            "email": "tester123@user.com",
            "password": "Password@123",
            "username": "tester123"
        })

        response = self.client.post(reverse('login'), {
            "email": "tester123@user.com",
            "password": "Password@123"
        })

        token = response.data['tokens']['access']
        #pass credentials to client with access token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


    def test_get_public_notes(self):
        """ Public notes can be accessed without authentication and returns right number of public notes"""
        response = self.client.get(reverse(getPublicNotes))
        num_items_returned = len(response.data)
        num_test_public_notes = len(self.public_notes)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(num_items_returned, num_test_public_notes )
        
    
    def test_get_user_notes_authenticated(self):
        """Authenticated user has access to their notes"""
        self.authenticate()
        response = self.client.get(reverse(getNotes))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_notes_not_authenticated(self):
        """Unauthenticated user has no access to notes"""
        response = self.client.get(reverse(getNotes))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_note_success(self):
        """Authenticated user can create Note successfully"""
        self.authenticate()
        sample_note = self.sample_note
        response = self.client.post(reverse("addNote"), sample_note)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], sample_note['title'])

    def test_delete_note(self):
        """Authenticated User can delete note"""
        self.authenticate()
        sample_note = self.sample_note
        response = self.client.post(reverse("addNote"), sample_note)
        note_id = response.data['id']
        response = self.client.delete(reverse(deleteNote, kwargs={"pk":note_id}))
        try:
            Note.objects.get(id=note_id)
        except:
            note_deleted = True
        else:
            note_deleted = False
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(note_deleted)

    def test_update_note(self):
        """Authenticated User can update note"""
        self.authenticate()
        sample_note = self.sample_note
        response = self.client.post(reverse("addNote"), sample_note)
        note_id = response.data['id']
        update_data = {
            "title": "updated",
            "body": "updated"
        }
        response = self.client.post(reverse(updateNote, kwargs={"pk":note_id}), update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], update_data['title'])

    def test_filter_note(self):
        """Notes can be filtered with a given tag"""
        self.authenticate()
        #add 4 sample notes. 2 tagged blue and 2 tagged black
        self.client.post(reverse("addNote"), self.sample_note)
        self.client.post(reverse("addNote"), self.sample_note2)
        self.client.post(reverse("addNote"), self.sample_note3)
        self.client.post(reverse("addNote"), self.sample_note4)
        tag1 = "blue"
        tag2 = "black"
        tag1_id = Tag.objects.get(name=tag1).id
        tag2_id = Tag.objects.get(name=tag2).id
        invalid_tag = "red"
        #filter for tag1 notes
        response = self.client.get(reverse(filterNotes, kwargs={"pk":tag1}))
        num_tag1_returned = len(response.data)
        filtered_tag1_correctly = True
        for data in response.data:
            if tag1_id not in data['tags']:
                filtered_tag1_correctly = False

        #filter for tag2 notes
        response = self.client.get(reverse(filterNotes, kwargs={"pk":tag2}))
        num_tag2_returned = len(response.data)
        filtered_tag2_correctly = True
        for data in response.data:
            if tag2_id not in data['tags']:
                filtered_tag2_correctly = False
        #invalid tag
        response = self.client.get(reverse(filterNotes, kwargs={"pk":invalid_tag}))
        self.assertEqual(num_tag1_returned, 2)
        self.assertEqual(num_tag2_returned, 2)
        self.assertTrue(filtered_tag1_correctly)
        self.assertTrue(filtered_tag2_correctly)
        self.assertEqual(response.data['message'], 'Invalid Tag')
        
    def test_search_notes(self):
        """Search notes with keyword"""
        self.authenticate()
        self.client.post(reverse("addNote"), self.sample_note)
        self.client.post(reverse("addNote"), self.sample_note2)
        self.client.post(reverse("addNote"), self.sample_note3)
        self.client.post(reverse("addNote"), self.sample_note4)
        key1 = "sample"
        key2 = "blue"
        response = self.client.get(reverse(search, kwargs={"keyword":key1}))
        num_notes_key1 = len(response.data)
        notes_contain_key = True
        for data in response.data:
            if key1 not in data['body']:
                notes_contain_key = False
        response = self.client.get(reverse(search, kwargs={"keyword":key2}))
        num_notes_key2 = len(response.data)
        notes_contain_key2 = True
        for data in response.data:
            if key2 not in data['body']:
                notes_contain_key2 = False
        self.assertEqual(num_notes_key1, 4)
        self.assertEqual(num_notes_key2, 2)
        self.assertTrue(notes_contain_key)
        self.assertTrue(notes_contain_key2)

    def test_get_private_note(self):
        self.authenticate()
        sample_note = self.sample_note
        response = self.client.post(reverse("addNote"), sample_note)
        note_id = response.data['id']
        note_title = response.data['title']
        response = self.client.get(reverse(getNote, kwargs={"pk": note_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(note_id, response.data['id'])
        self.assertEqual(note_title, response.data['title'])