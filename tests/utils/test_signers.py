# %% IMPORTS

from bikes.core import schemas
from bikes.utils import signers

# %% SIGNERS


def test_infer_signer(inputs: schemas.Inputs, outputs: schemas.Outputs) -> None:
    # given
    signer = signers.InferSigner()
    # when
    signature = signer.sign(inputs=inputs, outputs=outputs)
    # then
    assert set(signature.inputs.input_names()) == set(
        inputs.columns
    ), "Signature inputs should contain input column names."
    assert set(signature.outputs.input_names()) == set(
        outputs.columns
    ), "Signature outputs should contain output column names."
