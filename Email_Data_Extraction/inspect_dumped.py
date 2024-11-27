import email
import email.parser
import email.message
import email.policy

target_file = "dumped/grab.com-19283eb73c579a51.eml"
with open(target_file, "rb") as f:
    parser = email.parser.BytesParser(
        email.message.EmailMessage, policy=email.policy.default
    )
    data = parser.parse(f)

from extractors.base_extractor import EmailContent

content = EmailContent(data)

print(content)

print(content.get_plaintext())

from extractors.grab import GrabExtractor

print(GrabExtractor().extract(content))
