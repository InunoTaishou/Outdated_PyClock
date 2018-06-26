from gpiozero import MotionSensor
from io import BytesIO
from email import encoders
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import tempfile
from picamera import PiCamera
import threading
import datetime
import time
import os
import smtplib
import ntpath
import zipfile


class Email:
    def __init__(self, images, body, archive=False):
        self.on = True
        self.gmail = smtplib.SMTP('smtp.gmail.com', 587)
        self.gmail.starttls()
        self.gmail.login('PiClockAlerts@gmail.com', 'piclock1226')
        self.max_file_size = 25165824   # 25MB
        self.msg = MIMEMultipart()
        self.msg['Subject'] = 'PyClock Alert'
        self.msg['From'] = 'PiClockAlerts@gmail.com'
        self.msg['To'] = 'KyleHuskisson@gmail.com'
        self.msg.preamble = 'Alert from home PiClock'
        self.msg.attach(MIMEText(body, 'plain'))

        if archive:
            attachment = MIMEBase('application', 'zip')

            self.zip_file_name = self.date_stamp() + '.txt'

            self.tmp = tempfile.TemporaryFile(prefix=self.date_stamp(), suffix='.txt')

            self.zip_file = zipfile.ZipFile(self.tmp, 'w', zipfile.ZIP_LZMA)
            current_size = 0

            for image in images:
                if not self.on:
                    return self.__close()

                current_size += os.path.getsize(image)
                # 25MB file size
                if current_size > self.max_file_size:
                    print(self.time_stamp() + ' Size limit will exceed, no more images will be archived')
                    break
                else:
                    print(self.time_stamp() + ' Archiving file {} - {}'.format(i, ntpath.basename(image)))
                    self.zip_file.write(image, ntpath.basename(image))

            self.zip_file.close()

            self.tmp.seek(0)
            attachment.set_payload(self.tmp.read())
            self.tmp.close()
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', 'attachment', filename=self.zip_file_name)
            self.msg.attach(attachment)

        else:
            for image in images:
                if not self.on:
                    return self.__close()
                with open(image, 'rb') as fp:
                    attachment = MIMEImage(fp.read())
                    fp.close()
                    attachment.add_header('Content-Disposition', 'attachment: filename=' + ntpath.basename(image))
                    self.msg.attach(attachment)

        if not self.on:
            return self.__close()

        self.gmail.send_message(self.msg)
        self.__close()
        
    def __close(self):
        if self.zip_file:
            self.zip_file.close()
        if self.tmp:
            self.tmp.close()

        return self.gmail.quit()

    def date_stamp(self):
        return datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')


class SecurityCamera:
    def __init__(self):
        self.my_stream = BytesIO()
        self.pir = MotionSensor(4)
        self.camera = PiCamera(resolution=(1920, 1080))
        self.images_directory = self.current_images_directory() + os.sep + 'camera images' + os.sep
        self.on = False
        self.threads = []

        if not os.path.exists(self.images_directory):
            os.makedirs(self.images_directory)

    def start(self):
        if self.pir.motion_detected:
            print(self.time_stamp() + ' - Initializing motion sensor... Please wait')
            self.pir.wait_for_no_motion()

        print(self.time_stamp() + ' - Initialized')

        time.sleep(30)
        self.on = True
        self.main_loop()

    def stop(self):
        self.on = False

    def main_loop(self):
        while self.on:
            if True:
                images_captured = []
                old_stamp = self.time_stamp()

                while self.pir.motion_detected:
                    stamp = old_stamp
                    self.camera.annotate_text = stamp
                    self.camera.capture(self.images_directory + stamp + '.jpg')
                    # Draw the time stamp on the image
                    # Save the image
                    images_captured.append(self.images_directory + stamp + '.jpg')
                    print(self.images_directory + stamp + '.jpg')

                    while old_stamp == stamp:
                        time.sleep(0.1)
                        old_stamp = self.time_stamp()

                    if len(images_captured) == 15:
                        t = threading.Thread(target=Email,
                                             args=(images_captured, 'Dear Kyle,\n\nIntruder detected.', False))
                        t.start()
                        self.threads.append(t)

                t = threading.Thread(target=self.__email, args=((), 'Intruder left: ' + self.time_stamp(), False))
                t.start()
                self.on = False

            time.sleep(0.5)

    def time_stamp(self):
        return datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')

    def current_images_directory(self):
        return os.path.dirname((os.path.realpath(__file__)))

