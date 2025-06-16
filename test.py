from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class FacebookUrduTranslator:
    def __init__(self, model_name="facebook/nllb-200-distilled-600M"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.src_lang = "eng_Latn"
        self.tgt_lang = "urd_Arab"
        self.tokenizer.src_lang = self.src_lang
        # Manually map language codes to BOS token IDs if needed
        self.lang_code_to_id = {
            "eng_Latn": self.tokenizer.convert_tokens_to_ids("eng_Latn"),
            "urd_Arab": self.tokenizer.convert_tokens_to_ids("urd_Arab"),
        }

    def translate(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        if self.tgt_lang not in self.lang_code_to_id:
            raise ValueError(f"Target language '{self.tgt_lang}' is not supported.")
        forced_bos_token_id = self.lang_code_to_id[self.tgt_lang]
        generated_tokens = self.model.generate(**inputs, forced_bos_token_id=forced_bos_token_id)
        return self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

# Example usage
if __name__ == "__main__":
    translator = FacebookUrduTranslator()
    english_story = "This is a story about technology and how it is shaping the future of Pakistan."
    urdu_translation = translator.translate(english_story)
    
    print("\n--- English ---\n", english_story)
    print("\n--- Urdu ---\n", urdu_translation)
