import axios from 'axios';

const fetchModels = async () => {
  const { data } = await axios.get('models/');
  return data.reduce((models, model) => {
    const modifiedModel = {
      ...model,
      email: model.authors[0].email,
    };

    return {
      ...models,
      [model.database_name]: modifiedModel,
    };
  }, {});
};

export default { fetchModels };
