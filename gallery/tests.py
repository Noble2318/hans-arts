from decimal import Decimal
from io import BytesIO
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.contrib.admin.models import ADDITION, CHANGE, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from PIL import Image

from .models import ArtistProfile, ContactMessage, Painting
from .translations import TRANSLATIONS


class PublicPageTests(TestCase):
	def test_painting_image_and_video_uploads_are_saved(self):
		with TemporaryDirectory() as media_root:
			with override_settings(MEDIA_ROOT=media_root):
				image_buffer = BytesIO()
				Image.new('RGB', (1, 1)).save(image_buffer, format='PNG')
				painting = Painting.objects.create(
					title='Uploaded artwork',
					image=ContentFile(image_buffer.getvalue(), name='artwork.png'),
					video=ContentFile(b'video content', name='artwork.mp4'),
				)

				try:
					self.assertTrue(painting.image.storage.exists(painting.image.name))
					self.assertTrue(painting.video.storage.exists(painting.video.name))
				finally:
					painting.image.delete(save=False)
					painting.video.delete(save=False)
					painting.delete()

	def test_public_pages_render(self):
		for path in ('/', '/gallery/', '/about/', '/contact/'):
			with self.subTest(path=path):
				self.assertEqual(self.client.get(path).status_code, 200)

	def test_homepage_uses_artist_profile_and_shows_featured_art_once(self):
		ArtistProfile.objects.create(
			name='Amina Artist',
			bio='Stories inspired by the natural world.',
			whatsapp_number='0700123456',
		)
		painting = Painting.objects.create(
			title='Featured painting',
			image='paintings/featured.jpg',
			is_featured=True,
		)

		response = self.client.get(reverse('home'))

		self.assertContains(response, 'aria-label="Hanslim Art home"')
		self.assertContains(response, 'alt="Hanslim Art emblem"')
		self.assertRegex(
			response.content.decode(),
			r'<img[^>]+src="/static/gallery/images/hanslim-art-mark[^"]+\.svg"',
		)
		self.assertContains(response, 'Hanslim')
		self.assertContains(response, 'Amina Artist')
		self.assertContains(response, 'Explore the gallery')
		self.assertContains(response, 'Meet the artist')
		self.assertContains(
			response,
			'Where every brushstroke brings Africa&#x27;s stories to life.',
		)
		self.assertNotContains(response, 'Django does not read a variable tag split')
		self.assertContains(response, 'https://wa.me/255700123456')
		self.assertEqual(response.content.decode().count('class="whatsapp-float"'), 1)
		self.assertEqual(response.content.decode().count('Featured painting'), 1)
		self.assertNotContains(
			response,
			f'href="{reverse("painting_detail", args=[painting.pk])}"',
		)

	def test_contact_page_shows_branding_and_whatsapp_action(self):
		ArtistProfile.objects.create(
			name='Amina Artist',
			whatsapp_number='0700123456',
		)

		response = self.client.get(reverse('contact'))

		self.assertContains(response, 'class="contact-brand-lockup"')
		self.assertContains(response, 'alt=""')
		self.assertContains(response, 'class="btn contact-whatsapp"')
		self.assertContains(response, 'https://wa.me/255700123456')
		self.assertContains(response, 'class="whatsapp-float"')

	def test_contact_page_shows_buying_steps_and_order_action(self):
		response = self.client.get(reverse('contact'))

		self.assertContains(response, 'class="buying-guide__steps"')
		self.assertContains(response, 'class="buying-guide__step-number" aria-hidden="true">01</span>')
		self.assertContains(response, 'class="buying-guide__step-number" aria-hidden="true">04</span>')
		self.assertContains(
			response,
			'href="/contact/?inquiry_type=order#contact-form"',
		)

	def test_footer_shows_configured_social_media_icons(self):
		ArtistProfile.objects.create(
			name='Amina Artist',
			whatsapp_number='0700123456',
			instagram_url='https://www.instagram.com/hanslimart/',
			tiktok_url='https://www.tiktok.com/@hanslimart',
			x_url='https://x.com/hanslimart',
		)

		response = self.client.get(reverse('home'))

		self.assertContains(response, 'class="footer-grid"')
		self.assertContains(response, 'class="footer-logo"')
		self.assertContains(response, 'class="footer-bottom"')
		self.assertContains(response, 'href="#top"')
		self.assertContains(response, '<h3>Quick links</h3>')
		self.assertContains(response, '<h3>Follow</h3>')
		for label, url in (
			('Instagram', 'https://www.instagram.com/hanslimart/'),
			('TikTok', 'https://www.tiktok.com/@hanslimart'),
			('X', 'https://x.com/hanslimart'),
		):
			with self.subTest(platform=label):
				self.assertContains(response, f'href="{url}"')
				self.assertContains(response, f'>{label}</a>')
		self.assertNotContains(response, 'href="#"')

	def test_footer_shows_contact_details_and_hides_unconfigured_social_links(self):
		ArtistProfile.objects.create(
			name='Amina Artist',
			whatsapp_number='0700123456',
			email='amina@example.com',
		)

		response = self.client.get(reverse('home'))

		self.assertContains(response, 'mailto:amina@example.com')
		self.assertContains(response, 'https://wa.me/255700123456')
		self.assertContains(response, 'href="#top"')
		self.assertContains(response, 'Browse paintings')
		self.assertNotContains(response, '{{')
		self.assertNotContains(response, 'footer_browse')
		self.assertNotContains(response, '<h3>Follow</h3>')

	def test_footer_copy_is_available_in_every_supported_language(self):
		footer_keys = (
			'footer_tagline',
			'footer_quick_links',
			'footer_contact',
			'footer_reply_time',
			'footer_follow',
			'footer_rights',
			'footer_artwork_notice',
			'back_to_top',
		)

		for language, translations in TRANSLATIONS.items():
			with self.subTest(language=language):
				self.assertTrue(
					all(key in translations and translations[key] != key for key in footer_keys)
				)
				session = self.client.session
				session['language'] = language
				session.save()
				response = self.client.get(reverse('home'))
				self.assertEqual(response.status_code, 200)
				for key in footer_keys:
					self.assertNotContains(response, key)

	def test_about_page_shows_artist_story_details(self):
		ArtistProfile.objects.create(
			name='Amina Artist',
			bio='Stories inspired by the natural world.',
			whatsapp_number='0700123456',
			tagline='Painting stories from home.',
			materials='Acrylic on canvas.',
			inspiration='Wildlife and family stories.',
		)

		response = self.client.get(reverse('about'))

		self.assertContains(response, 'Painting stories from home.')
		self.assertContains(response, 'Acrylic on canvas.')
		self.assertContains(response, 'Wildlife and family stories.')
		self.assertContains(
			response,
			'Browse the gallery or message the artist directly',
		)
		self.assertNotContains(response, '{{ t.about_cta_text')

	def test_order_a_painting_opens_prefilled_order_form_and_saves_order(self):
		response = self.client.get(
			reverse('contact'),
			{'inquiry_type': 'order'},
		)

		self.assertContains(response, 'Order a painting')
		self.assertContains(response, '<option value="order" selected>')
		self.assertContains(response, 'What would you like painted?')

		response = self.client.post(
			reverse('contact'),
			{
				'name': 'Alex Customer',
				'email': 'alex@example.com',
				'phone': '0712345678',
				'inquiry_type': 'order',
				'order_details': 'A large lion painting in sunset colours.',
				'message': 'Please let me know the price.',
			},
		)

		self.assertRedirects(response, reverse('contact'))
		order = ContactMessage.objects.get(name='Alex Customer')
		self.assertEqual(order.inquiry_type, 'order')
		self.assertEqual(
			order.order_details,
			'A large lion painting in sunset colours.',
		)
		self.assertIsNone(order.related_painting)

	def test_custom_painting_order_requires_a_description(self):
		response = self.client.post(
			reverse('contact'),
			{
				'name': 'Alex Customer',
				'email': 'alex@example.com',
				'inquiry_type': 'order',
				'order_details': '',
				'message': 'I want a painting.',
			},
		)

		self.assertContains(
			response,
			'Please describe the picture you would like to order.',
		)
		self.assertFalse(ContactMessage.objects.exists())

	def test_painting_detail_form_can_save_an_order_about_that_painting(self):
		painting = Painting.objects.create(
			title='Kilimanjaro',
			image='paintings/kilimanjaro.jpg',
		)

		response = self.client.post(
			reverse('painting_detail', args=[painting.pk]),
			{
				'name': 'Alex Customer',
				'inquiry_type': 'order',
				'order_details': 'A smaller version with warmer colours.',
				'message': 'Can this be made to order?',
			},
		)

		self.assertRedirects(
			response,
			reverse('painting_detail', args=[painting.pk]),
		)
		order = ContactMessage.objects.get(name='Alex Customer')
		self.assertEqual(order.inquiry_type, 'order')
		self.assertEqual(order.related_painting, painting)

	def test_artwork_details_highlight_availability_and_contact_actions(self):
		ArtistProfile.objects.create(
			name='Amina Artist',
			bio='Stories inspired by the natural world.',
			whatsapp_number='0700123456',
		)
		painting = Painting.objects.create(
			title='Wildlife Study',
			image='paintings/wildlife-study.jpg',
			medium='Acrylic on canvas',
			size='60cm x 80cm',
			price=Decimal('125000.00'),
			currency='USD',
			video='paintings/videos/wildlife-study.mp4',
		)

		response = self.client.get(
			reverse('painting_detail', args=[painting.pk]),
		)

		self.assertContains(response, 'class="artwork-status is-available"')
		self.assertContains(response, 'Acrylic on canvas')
		self.assertContains(response, '60cm x 80cm')
		self.assertContains(response, 'USD 125000.00')
		self.assertContains(response, 'data-video-src="/media/paintings/videos/wildlife-study.mp4"')
		self.assertContains(response, 'id="lightbox-video"')
		self.assertContains(response, 'https://wa.me/255700123456')
		self.assertContains(response, 'Wildlife%20Study')
		self.assertContains(response, 'id="artwork-inquiry"')

	def test_new_story_and_contact_labels_exist_for_every_language(self):
		keys = (
			'meet_the_artist',
			'video_for_artwork',
			'explore_gallery',
			'contact_artist',
			'artist_intro',
			'whatsapp_message',
			'about_materials',
			'about_inspiration',
			'about_cta_title',
			'about_cta_text',
			'order_painting',
			'inquiry_type',
			'general_inquiry',
			'painting_order',
			'order_details',
			'order_details_help',
			'order_details_required',
			'filter_category',
			'filter_availability',
			'filter_currency',
			'filter_min_price',
			'filter_max_price',
			'filter_apply',
			'filter_clear',
			'category_wanyama',
			'category_traditional',
			'category_other',
			'invalid_price',
			'price_range_error',
			'price_currency_required',
			'invalid_filters',
		)

		for language, translations in TRANSLATIONS.items():
			for key in keys:
				with self.subTest(language=language, key=key):
					self.assertIn(key, translations)
					self.assertNotEqual(translations[key], key)

	def test_contact_placeholders_are_english_by_default(self):
		response = self.client.get('/contact/')

		self.assertEqual(response.context['current_lang'], 'en')
		for placeholder in ('Your name', 'Email (optional)', 'Phone number', 'Your message'):
			with self.subTest(placeholder=placeholder):
				self.assertContains(response, f'placeholder="{placeholder}"')

	def test_gallery_search_placeholder_stays_english_in_other_languages(self):
		session = self.client.session
		session['language'] = 'sw'
		session.save()

		response = self.client.get('/gallery/')

		self.assertContains(response, 'placeholder="Search paintings..."')

	def test_gallery_filters_combine_search_category_availability_and_price(self):
		matching = Painting.objects.create(
			title='Golden Savannah',
			image='paintings/golden-savannah.jpg',
			description='A lion in warm evening light.',
			category='wanyama',
			price=Decimal('125000.00'),
			is_available=True,
		)
		Painting.objects.create(
			title='Savannah at Night',
			image='paintings/savannah-night.jpg',
			category='wanyama',
			price=Decimal('125000.00'),
			is_available=False,
		)
		Painting.objects.create(
			title='Golden Tradition',
			image='paintings/golden-tradition.jpg',
			category='traditional',
			price=Decimal('125000.00'),
			is_available=True,
		)
		Painting.objects.create(
			title='Golden Sky',
			image='paintings/golden-sky.jpg',
			category='wanyama',
			price=Decimal('250000.00'),
			is_available=True,
		)

		response = self.client.get(
			reverse('gallery_list'),
			{
				'q': 'golden',
				'category': 'wanyama',
				'availability': 'available',
				'min_price': '100000',
				'max_price': '150000',
				'currency': 'TZS',
			},
		)

		self.assertEqual(
			list(response.context['paintings']),
			[matching],
		)
		self.assertContains(response, 'value="golden"')
		self.assertContains(response, 'value="100000"')

	def test_gallery_availability_filter_includes_unpriced_sold_art(self):
		sold = Painting.objects.create(
			title='Sold sketch',
			image='paintings/sold-sketch.jpg',
			price=None,
			is_available=False,
		)
		Painting.objects.create(
			title='Available sketch',
			image='paintings/available-sketch.jpg',
			price=Decimal('50000.00'),
			is_available=True,
		)

		response = self.client.get(
			reverse('gallery_list'),
			{'availability': 'sold'},
		)

		self.assertEqual(list(response.context['paintings']), [sold])

	def test_gallery_price_filters_report_invalid_ranges_and_return_no_results(self):
		Painting.objects.create(
			title='Painting',
			image='paintings/painting.jpg',
			price=Decimal('100000.00'),
		)

		response = self.client.get(
			reverse('gallery_list'),
			{'min_price': '200000', 'max_price': '100000'},
		)

		self.assertContains(response, 'Minimum price must not exceed maximum price.')
		self.assertEqual(list(response.context['paintings']), [])

	def test_gallery_price_filter_requires_and_respects_selected_currency(self):
		tzs_painting = Painting.objects.create(
			title='TZS painting',
			image='paintings/tzs-painting.jpg',
			price=Decimal('100000.00'),
			currency='TZS',
		)
		usd_painting = Painting.objects.create(
			title='USD painting',
			image='paintings/usd-painting.jpg',
			price=Decimal('100000.00'),
			currency='USD',
		)

		response = self.client.get(
			reverse('gallery_list'),
			{'min_price': '50000'},
		)
		self.assertContains(response, 'Choose a currency before filtering by price.')

		response = self.client.get(
			reverse('gallery_list'),
			{'min_price': '50000', 'currency': 'USD'},
		)
		self.assertEqual(list(response.context['paintings']), [usd_painting])
		self.assertNotIn(tzs_painting, response.context['paintings'])

	def test_gallery_pagination_preserves_active_filters(self):
		for index in range(10):
			Painting.objects.create(
				title=f'Wildlife painting {index}',
				image=f'paintings/wildlife-{index}.jpg',
				category='wanyama',
				price=Decimal('100000.00'),
				is_available=True,
			)

		response = self.client.get(
			reverse('gallery_list'),
			{
				'category': 'wanyama',
				'availability': 'available',
				'min_price': '50000',
				'currency': 'TZS',
			},
		)

		self.assertContains(
			response,
			'?category=wanyama&amp;availability=available&amp;min_price=50000&amp;currency=TZS&amp;page=2',
		)

	def test_invalid_saved_language_defaults_to_english(self):
		session = self.client.session
		session['language'] = 'unsupported'
		session.save()

		response = self.client.get('/')

		self.assertEqual(response.context['current_lang'], 'en')
		self.assertContains(response, 'lang="en"')

	def test_language_selector_reflects_the_saved_language(self):
		session = self.client.session
		session['language'] = 'fr'
		session.save()

		response = self.client.get(reverse('home'))

		self.assertRegex(
			response.content.decode(),
			r'<option\s+value="fr"\s+selected',
		)

	def test_missing_page_uses_custom_404(self):
		response = self.client.get('/missing-page/')

		self.assertEqual(response.status_code, 404)
		self.assertContains(response, '404 - Page Not Found', status_code=404)
		content = response.content.decode()
		self.assertIn('class="site-header"', content)
		self.assertIn('This canvas is blank', content)
		self.assertIn('href="/"', content)
		self.assertIn('href="/gallery/"', content)

	def test_language_switch_rejects_external_redirect(self):
		response = self.client.get(
			reverse('set_language'),
			{'lang': 'fr', 'next': 'https://evil.example'},
		)

		self.assertRedirects(response, '/', fetch_redirect_response=False)
		self.assertEqual(self.client.session['language'], 'fr')

	def test_language_switch_allows_local_redirect(self):
		response = self.client.get(
			reverse('set_language'),
			{'lang': 'fr', 'next': '/contact/'},
		)

		self.assertRedirects(response, '/contact/', fetch_redirect_response=False)


class PaintingAdminDeletionTests(TestCase):
	def setUp(self):
		self.admin_user = get_user_model().objects.create_superuser(
			username='admin',
			email='admin@example.com',
			password='password',
		)
		self.client.force_login(self.admin_user)

	def test_painting_admin_exposes_tzs_and_usd_currency_choices(self):
		response = self.client.get(reverse('admin:gallery_painting_add'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '<option value="TZS" selected>TZS</option>')
		self.assertContains(response, '<option value="USD">USD</option>')

	def create_painting_history(self, painting):
		content_type = ContentType.objects.get_for_model(Painting)
		for action_flag in (ADDITION, CHANGE):
			LogEntry.objects.create(
				user=self.admin_user,
				content_type=content_type,
				object_id=str(painting.pk),
				object_repr=painting.title,
				action_flag=action_flag,
				change_message='',
			)

	def test_deleting_painting_removes_all_recent_action_entries(self):
		painting = Painting.objects.create(
			title='Painting to delete',
			image='paintings/to-delete.jpg',
		)
		self.create_painting_history(painting)

		response = self.client.post(
			reverse('admin:gallery_painting_delete', args=[painting.pk]),
			{'post': 'yes'},
		)

		self.assertRedirects(response, reverse('admin:gallery_painting_changelist'))
		self.assertFalse(Painting.objects.filter(pk=painting.pk).exists())
		self.assertFalse(
			LogEntry.objects.filter(
				content_type=ContentType.objects.get_for_model(Painting),
				object_id=str(painting.pk),
			).exists()
		)

	def test_bulk_deleting_paintings_removes_all_recent_action_entries(self):
		paintings = [
			Painting.objects.create(
				title=f'Painting {index}',
				image=f'paintings/{index}.jpg',
			)
			for index in range(2)
		]
		for painting in paintings:
			self.create_painting_history(painting)

		response = self.client.post(
			reverse('admin:gallery_painting_changelist'),
			{
				'action': 'delete_selected',
				'_selected_action': [painting.pk for painting in paintings],
				'index': 0,
				'post': 'yes',
			},
		)

		self.assertRedirects(response, reverse('admin:gallery_painting_changelist'))
		for painting in paintings:
			self.assertFalse(Painting.objects.filter(pk=painting.pk).exists())
			self.assertFalse(
				LogEntry.objects.filter(
					content_type=ContentType.objects.get_for_model(Painting),
					object_id=str(painting.pk),
				).exists()
			)
