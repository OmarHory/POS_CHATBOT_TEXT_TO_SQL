# WhatsApp Chatbot using Twilio and GPT

This is a sample chatbot application that demonstrates how to build a WhatsApp chatbot using Twilio and the GPT language model from OpenAI. The chatbot is designed to respond to natural language queries from users and generate responses using the GPT model.

## Getting Started

To use this chatbot, you will need to have a Twilio account and an API key for the GPT model. You will also need to set up a webhook to receive incoming messages from WhatsApp, you can navigate to Twilio for more information.

### Prerequisites

- Python 3.7 or higher
- A Twilio account
- An API key for the GPT model

### Installation

To install the chatbot, you can use the following command:

`python setup.py install`

## Usage

To run the chatbot, you can use the following command:

`sh rub_bot.sh`

This will start the chatbot and listen for incoming messages on the webhook URL.

## Configuration

To configure the chatbot, you can edit the `config.py` file. This file contains the configuration settings for the Twilio account and the GPT model API key.

## Twilio Integration

To integrate the chatbot with Twilio, you will need to set up a webhook that points to the `app.py` file. This file contains the code that handles incoming messages and generates responses using the GPT model & Flask API.

## GPT Integration

To integrate the chatbot with the GPT model, you will need to provide an API key for the model. This key should be stored in the `config.py` file.

## Customization

To customize the chatbot, you can modify the code in the `src\response_builder.py` file. This file contains the code that generates responses using the GPT model. You can modify this code to change the behavior of the chatbot or add new features.

## License

This chatbot is released under the MIT License. See the LICENSE file for more details.

## Contributors

- Omar Alhory (@OmarHory)
- Zeid Husban ()
- Wadi Hawi ()
- Zaid Farekh (@zaidfarekh)

## Acknowledgments

- The GPT model is provided by OpenAI (https://openai.com/)
- Twilio provides a powerful API for building chatbots (https://www.twilio.com/)
- Redis provides a powerful No-SQL database for handling user states (https://redis.io/)

Feel free to contribute by opening issues or pull requests!

More information will be added to this README.