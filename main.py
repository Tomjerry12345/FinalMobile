from __future__ import unicode_literals
import youtube_dl
from kivy.core.window import Window
from youtube_transcript_api import YouTubeTranscriptApi
from kivy.logger import Logger
from youtube_transcript_api.formatters import WebVTTFormatter
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.toast import toast
from kivy.clock import Clock
import threading


class MainLayout(Widget):
    url = ""
    video_id = ""

    def cari(self, url):
        self.url = url

        if self.url != "":
            ydl_opts = {}
            # link = 'https://www.youtube.com/watch?v=pZg3DIKxhXo'
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                # ydl.download([])
                info_dict = ydl.extract_info(self.url, download=False)
                thumbnail = info_dict.get("thumbnail", None)
                title_video = info_dict.get("title", None)
                self.video_id = info_dict.get("id", None)
                self.ids.thumbnail.source = thumbnail
                self.ids.title_video.text = title_video

        else:
            Logger.error("Url tidak boleh kosong")
            toast("Url tidak boleh kosong")

    def my_hook(self, d):
        if d['status'] == 'finished':
            toast("Download berhasil")
        if d['status'] == 'downloading':
            p = d['_percent_str']
            p = p.replace('%', '')
            # Logger.info(str(int(p)))
            self.ids.progress_bar.value = float(p)
            # print("test: ", float(p))
            # print(d['filename'], d['_percent_str'], d['_eta_str'])'

    # To continuesly increasing the value of pb.
    def next(self, dt):
        # if self.ids.progress_bar.value >= 100:
        #     toast("succes")
        # self.ids.progress_bar.value += 1
        if self.url != "":
            ydl_opts = {
                'progress_hooks': [self.my_hook]
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])

        else:
            toast("Video Tidak Ditemukan")

    def download_video(self):
        Clock.schedule_interval(self.next, 1 / 25)


    def download_subtitle(self):
        Logger.info(self.video_id)
        if self.video_id != "":
            formatter = WebVTTFormatter()
            # retrieve the available transcripts
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(self.video_id)

                # iterate over all available transcripts
                for transcript in transcript_list:
                    Logger.info("video_id : " + transcript.video_id)
                    Logger.info("language : " + transcript.language)
                    Logger.info("language_code : " + transcript.language_code)
                    Logger.info("is_generated : " + str(transcript.is_generated))
                    Logger.info("is_translatable : " + str(transcript.is_translatable))
                    Logger.info("translation_languages : " + str(transcript.translation_languages))

                    # fetch the actual transcript data
                    #     print(transcript.fetch())
                    #
                    #     # translating the transcript will return another transcript object
                    translate_result = transcript.translate('id').fetch()
                    vttFormatter = formatter.format_transcript(translate_result)
                    Logger.info("translate_indonesian : " + str(vttFormatter))

                    # Now we can write it out to a file.
                    with open(self.ids.title_video.text + '.srt', 'w', encoding='utf-8') as srt_file:
                        srt_file.write(vttFormatter)
                #
                # # you can also directly filter for the language you are looking for, using the transcript list
                # transcript = transcript_list.find_transcript(['de', 'en'])
                #
                # # or just filter for manually created transcripts
                # transcript = transcript_list.find_manually_created_transcript(['de', 'en'])
                #
                # # or automatically generated ones
                # transcript = transcript_list.find_generated_transcript(['de', 'en'])

            except:
                toast("Subtitle tidak di temukan")



        else:
            toast("Video Tidak Ditemukan")


class YoutubeDownloaderApp(MDApp):
    def build(self):
        Window.size = [300, 600]
        return MainLayout()


if __name__ == '__main__':
    YoutubeDownloaderApp().run()
