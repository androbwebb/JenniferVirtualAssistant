import html2text
from abc import abstractproperty


class JenniferResponse(object):
    """A full response, made up of segments"""
    def __init__(self, response_creator, segments):
        if isinstance(response_creator, str):
            self.response_creator = response_creator
        else:
            self.response_creator = response_creator.__class__.__name__
        self.segments = segments

    def _to_format(self, to_format='text'):
        to_format = to_format.lower()

        if to_format == 'text':
            func = 'to_text'
        elif to_format == 'html':
            func = 'to_html'
        elif to_format == 'dict':
            func = 'to_dict'
            return [getattr(segment, func) for segment in self.segments]
        else:
            raise Exception(f'Attempting to format {self.__class__} object to a non-implemented format')

        return " ".join([getattr(segment, func) for segment in self.segments])

    def filter_responses(self, allowed_data_types):
        self.segments = [segment for segment in self.segments if segment.__class__ in allowed_data_types]

    def to_html(self):
        return self._to_format('html')

    def to_text(self):
        return self._to_format('text')

    @property
    def to_dict(self):
        return self.__dict__


class JenniferResponseAbstractSegment(object):
    @abstractproperty
    def response_type(self):
        pass

    @abstractproperty
    def to_html(self):
        return self.to_text()

    @abstractproperty
    def to_text(self):
        pass

    @property
    def to_dict(self):
        return self.__dict__


class JenniferTextResponseSegment(JenniferResponseAbstractSegment):
    """A Plaintext response segment"""
    def __init__(self, text):
        self.text = text

    @property
    def response_type(self):
        return 'text'

    @property
    def to_text(self):
        try:
            return str(self.text)
        except UnicodeDecodeError:
            # http://stackoverflow.com/questions/4237898/unicodedecodeerror-ascii-codec-cant-decode-byte-0xe0-in-position-0-ordinal
            return ""


class JenniferImageReponseSegment(JenniferResponseAbstractSegment):
    """An Image response segment"""
    def __init__(self, link, alternate_text):
        self.link = link
        self.alternate_text = alternate_text

    @property
    def response_type(self):
        return 'image'

    @property
    def to_html(self):
        return "<img src='{link}' alt='{alternate_text}/>".format(link=self.link, alternate_text=self.alternate_text)

    @property
    def to_text(self):
        return u"[Image: {alternate_text}]".format(alternate_text=self.alternate_text)


class JenniferLinkResponseSegement(JenniferTextResponseSegment):
    def __init__(self, text, link):
        JenniferTextResponseSegment.__init__(self, text)
        self.link = link

    @property
    def response_type(self):
        return 'link'

    @property
    def to_html(self):
        return "<a href='{link}'>{text}</a>".format(link=self.link, text=self.text)

    @property
    def to_text(self):
        return self.link


class JenniferHtmlResponseSegment(JenniferResponseAbstractSegment):
    def __init__(self, html):
        self.html = html

    @property
    def response_type(self):
        return 'html'

    @property
    def to_html(self):
        return self.html

    @property
    def to_text(self):
        return html2text.html2text(self.html)


ALL_RESPONSE_TYPES = JenniferResponseAbstractSegment.__subclasses__
