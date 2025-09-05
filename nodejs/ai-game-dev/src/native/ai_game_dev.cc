// Native Node.js bindings for AI Game Development library
#include <nan.h>
#include <string>
#include <memory>
#include <vector>

extern "C" {
    // External C functions from Go shared library
    int ai_game_dev_init();
    int ai_game_dev_create_game(const char* description, const char* config);
    const char* ai_game_dev_get_result(int instance_id);
    const char* ai_game_dev_supported_engines();
    const char* ai_game_dev_version();
    const char* ai_game_dev_get_last_error();
    void ai_game_dev_cleanup();
}

// Initialize the native library
class InitWorker : public Nan::AsyncWorker {
public:
    InitWorker(Nan::Callback *callback) : Nan::AsyncWorker(callback), result(0) {}
    
    void Execute() override {
        result = ai_game_dev_init();
    }
    
    void HandleOKCallback() override {
        Nan::HandleScope scope;
        v8::Local<v8::Value> argv[] = {
            Nan::Null(),
            Nan::New<v8::Boolean>(result == 0)
        };
        callback->Call(2, argv, async_resource);
    }
    
private:
    int result;
};

// Create game asynchronously
class CreateGameWorker : public Nan::AsyncWorker {
public:
    CreateGameWorker(Nan::Callback *callback, const std::string &desc, const std::string &config)
        : Nan::AsyncWorker(callback), description(desc), config_json(config), instance_id(-1) {}
    
    void Execute() override {
        instance_id = ai_game_dev_create_game(description.c_str(), config_json.c_str());
        if (instance_id < 0) {
            error_message = ai_game_dev_get_last_error();
        } else {
            result_json = ai_game_dev_get_result(instance_id);
        }
    }
    
    void HandleOKCallback() override {
        Nan::HandleScope scope;
        
        if (instance_id < 0) {
            v8::Local<v8::Value> argv[] = {
                Nan::Error(error_message.c_str()),
                Nan::Null()
            };
            callback->Call(2, argv, async_resource);
        } else {
            // Parse JSON result
            v8::Local<v8::String> json_str = Nan::New(result_json).ToLocalChecked();
            Nan::MaybeLocal<v8::Value> maybe_result = Nan::JSON::Parse(json_str);
            
            if (maybe_result.IsEmpty()) {
                v8::Local<v8::Value> argv[] = {
                    Nan::Error("Failed to parse result JSON"),
                    Nan::Null()
                };
                callback->Call(2, argv, async_resource);
            } else {
                v8::Local<v8::Value> argv[] = {
                    Nan::Null(),
                    maybe_result.ToLocalChecked()
                };
                callback->Call(2, argv, async_resource);
            }
        }
    }
    
private:
    std::string description;
    std::string config_json;
    int instance_id;
    std::string result_json;
    std::string error_message;
};

// JavaScript function: initialize()
NAN_METHOD(Initialize) {
    if (info.Length() != 1 || !info[0]->IsFunction()) {
        return Nan::ThrowError("Expected callback function");
    }
    
    Nan::Callback *callback = new Nan::Callback(info[0].As<v8::Function>());
    Nan::AsyncQueueWorker(new InitWorker(callback));
}

// JavaScript function: createGame(description, config, callback)  
NAN_METHOD(CreateGame) {
    if (info.Length() != 3 || !info[0]->IsString() || !info[1]->IsObject() || !info[2]->IsFunction()) {
        return Nan::ThrowError("Expected (description: string, config: object, callback: function)");
    }
    
    // Convert description
    v8::String::Utf8Value description(info.GetIsolate(), info[0]);
    std::string desc(*description);
    
    // Convert config object to JSON
    v8::Local<v8::Object> config_obj = info[1]->ToObject(Nan::GetCurrentContext()).ToLocalChecked();
    Nan::MaybeLocal<v8::String> maybe_json = Nan::JSON::Stringify(config_obj);
    
    if (maybe_json.IsEmpty()) {
        return Nan::ThrowError("Failed to serialize config object");
    }
    
    v8::String::Utf8Value config_json(info.GetIsolate(), maybe_json.ToLocalChecked());
    std::string config(*config_json);
    
    Nan::Callback *callback = new Nan::Callback(info[2].As<v8::Function>());
    Nan::AsyncQueueWorker(new CreateGameWorker(callback, desc, config));
}

// JavaScript function: getSupportedEngines()
NAN_METHOD(GetSupportedEngines) {
    const char* engines_json = ai_game_dev_supported_engines();
    
    if (!engines_json) {
        return Nan::ThrowError("Failed to get supported engines");
    }
    
    v8::Local<v8::String> json_str = Nan::New(engines_json).ToLocalChecked();
    Nan::MaybeLocal<v8::Value> maybe_result = Nan::JSON::Parse(json_str);
    
    if (maybe_result.IsEmpty()) {
        return Nan::ThrowError("Failed to parse engines JSON");
    }
    
    info.GetReturnValue().Set(maybe_result.ToLocalChecked());
}

// JavaScript function: getVersion()
NAN_METHOD(GetVersion) {
    const char* version = ai_game_dev_version();
    info.GetReturnValue().Set(Nan::New(version).ToLocalChecked());
}

// JavaScript function: getLastError()
NAN_METHOD(GetLastError) {
    const char* error = ai_game_dev_get_last_error();
    info.GetReturnValue().Set(Nan::New(error).ToLocalChecked());
}

// JavaScript function: cleanup()
NAN_METHOD(Cleanup) {
    ai_game_dev_cleanup();
    info.GetReturnValue().Set(Nan::True());
}

// Module initialization
NAN_MODULE_INIT(InitModule) {
    // Export functions to JavaScript
    Nan::Set(target, Nan::New("initialize").ToLocalChecked(),
        Nan::GetFunction(Nan::New<v8::FunctionTemplate>(Initialize)).ToLocalChecked());
    
    Nan::Set(target, Nan::New("createGame").ToLocalChecked(),
        Nan::GetFunction(Nan::New<v8::FunctionTemplate>(CreateGame)).ToLocalChecked());
    
    Nan::Set(target, Nan::New("getSupportedEngines").ToLocalChecked(),
        Nan::GetFunction(Nan::New<v8::FunctionTemplate>(GetSupportedEngines)).ToLocalChecked());
    
    Nan::Set(target, Nan::New("getVersion").ToLocalChecked(),
        Nan::GetFunction(Nan::New<v8::FunctionTemplate>(GetVersion)).ToLocalChecked());
    
    Nan::Set(target, Nan::New("getLastError").ToLocalChecked(),
        Nan::GetFunction(Nan::New<v8::FunctionTemplate>(GetLastError)).ToLocalChecked());
    
    Nan::Set(target, Nan::New("cleanup").ToLocalChecked(),
        Nan::GetFunction(Nan::New<v8::FunctionTemplate>(Cleanup)).ToLocalChecked());
}

NODE_MODULE(ai_game_dev_native, InitModule)